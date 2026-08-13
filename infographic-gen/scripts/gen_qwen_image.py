#!/usr/bin/env python3
"""调用阿里云百炼 qwen-image-3.0-pro 生成信息图(同步接口).

用法:
  export DASHSCOPE_API_KEY=sk-...
  python gen_qwen_image.py PROMPT_FILE OUT_PATH [SIZE]

SIZE 默认 2560*1440 (横版三栏 16:9, 小字更清晰)。其他常用: 1664*928 (省额度, 1k 计费档) / 1024*1024 / 928*1664 (竖版长图)。

端点排雷:
  qwen-image-3.0-pro 只走 multimodal-generation/generation, 不走标准
  /text2image/image-synthesis (url error), 也不走 /compatible-mode (404)。
"""
import json
import os
import sys
import urllib.error
import urllib.request

URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
MODEL = "qwen-image-3.0-pro"


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


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    prompt_file, out_path = sys.argv[1], sys.argv[2]
    size = sys.argv[3] if len(sys.argv) > 3 else "2560*1440"

    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("[err] DASHSCOPE_API_KEY env var required", file=sys.stderr)
        sys.exit(2)

    with open(prompt_file, encoding="utf-8") as f:
        prompt = f.read().strip()
    print(f"[info] prompt: {len(prompt)} chars, size={size}, model={MODEL}",
          file=sys.stderr)

    payload = {
        "model": MODEL,
        "input": {
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        },
        "parameters": {"size": size, "n": 1},
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    resp = _urlopen(req)
    data = json.loads(resp.read())

    try:
        img_url = data["output"]["choices"][0]["message"]["content"][0]["image"]
    except (KeyError, IndexError):
        print("[err] image url not found in response:", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        sys.exit(3)

    print(f"[info] image url: {img_url}", file=sys.stderr)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    urllib.request.urlretrieve(img_url, out_path)
    print(f"[ok] saved -> {out_path}")
    usage = data.get("usage", {})
    if usage:
        print(f"[info] usage: {usage}", file=sys.stderr)


if __name__ == "__main__":
    main()
