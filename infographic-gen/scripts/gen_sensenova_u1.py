#!/usr/bin/env python3
"""调用 sensenova-u1-fast 生成信息图(商汤日日新, OpenAI 兼容).

用法:
  export SENSENOVA_KEY=sk-...                              # 平台 API key
  export SENSENOVA_GATEWAY=https://token.sensenova.cn/v1   # 可选, 默认就是这个
  export SENSENOVA_WATERMARK=false                         # 可选, 默认去水印; true 加官方 Logo 水印
  python gen_sensenova_u1.py PROMPT_FILE OUT_PATH [SIZE]

SIZE 默认 2752x1536 (横版三栏)。**注意分隔符是 x 不是 *(与 DashScope 的写法不同)。

报错速查:
  auth_unavailable: no auth available → 走自建兼容网关时上游凭证没配, 找网关维护方
  404                                  → base_url 写错(应指向 /v1)
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

MODEL = "sensenova-u1-fast"
DEFAULT_BASE = "https://token.sensenova.cn/v1"


def _urlopen(req):
    """发请求; 出错时打印服务端响应体(常含真实原因: 尺寸不合法/域名被拦/鉴权失败等),
    而不是丢一段裸 traceback."""
    try:
        return urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"[err] HTTP {e.code} {e.reason}", file=sys.stderr)
        if body.strip():
            print(body[:1500], file=sys.stderr)
        sys.exit(4)
    except urllib.error.URLError as e:
        print(f"[err] network error: {e.reason}", file=sys.stderr)
        sys.exit(5)


def resolve_endpoint():
    """SENSENOVA_GATEWAY 带不带 /v1 都行, 也可指向自建的 OpenAI 兼容网关."""
    base = (os.environ.get("SENSENOVA_GATEWAY") or DEFAULT_BASE).rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    return base + "/images/generations"


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    prompt_file, out_path = sys.argv[1], sys.argv[2]
    size = sys.argv[3] if len(sys.argv) > 3 else "2752x1536"

    api_key = os.environ.get("SENSENOVA_KEY")
    if not api_key:
        print("[err] SENSENOVA_KEY env var required", file=sys.stderr)
        sys.exit(2)

    # watermark=false 去水印(公测免费, 后续转付费); 显式传参避免官方默认值变更影响结果
    watermark = os.environ.get("SENSENOVA_WATERMARK", "false").strip().lower() in ("1", "true", "yes")

    endpoint = resolve_endpoint()
    with open(prompt_file, encoding="utf-8") as f:
        prompt = f.read().strip()
    print(f"[info] prompt: {len(prompt)} chars, size={size}, model={MODEL}, "
          f"watermark={watermark}", file=sys.stderr)

    payload = {"model": MODEL, "prompt": prompt, "size": size, "n": 1,
               "watermark": watermark}
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    print(f"[info] POST {endpoint}", file=sys.stderr)
    resp = _urlopen(req)
    data = json.loads(resp.read())

    items = data.get("data") or []
    if not items:
        print("[err] empty data array in response:", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        sys.exit(3)
    item = items[0]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    if "b64_json" in item:
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
        print(f"[ok] saved (b64) -> {out_path}")
    elif "url" in item:
        print(f"[info] image url: {item['url']}", file=sys.stderr)
        urllib.request.urlretrieve(item["url"], out_path)
        print(f"[ok] saved (url) -> {out_path}")
    else:
        print(f"[err] no b64_json / url. keys: {list(item.keys())}",
              file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
