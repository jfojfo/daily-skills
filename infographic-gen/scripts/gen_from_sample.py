#!/usr/bin/env python3
"""按序号从 prompts/samples_infographic.jsonl 取一条 prompt 并生成图.

用法:
  export DASHSCOPE_API_KEY=sk-...
  python gen_from_sample.py <INDEX> <OUT_PATH> [--provider qwen|sensenova]

默认 provider=qwen (qwen-image-3.0-pro)。
sensenova 走商汤日日新 (token.sensenova.cn), 需要 SENSENOVA_KEY;
自建 OpenAI 兼容网关可用 SENSENOVA_GATEWAY 覆盖 base_url。

样本里自带 width/height, 脚本会按样本指定尺寸出图。
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

SAMPLES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "prompts", "samples_infographic.jsonl",
)

QWEN_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
QWEN_MODEL = "qwen-image-3.0-pro"
SENSENOVA_MODEL = "sensenova-u1-fast"
SENSENOVA_BASE = "https://token.sensenova.cn/v1"


def resolve_sensenova_endpoint():
    """SENSENOVA_GATEWAY 带不带 /v1 都行, 也可指向自建的 OpenAI 兼容网关."""
    base = (os.environ.get("SENSENOVA_GATEWAY") or SENSENOVA_BASE).rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    return base + "/images/generations"


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


def load_sample(idx):
    samples = []
    with open(SAMPLES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    if not (0 <= idx < len(samples)):
        sys.exit(f"[err] index {idx} out of range (0..{len(samples)-1})")
    return samples[idx]


def gen_qwen(sample, out_path):
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        sys.exit("[err] DASHSCOPE_API_KEY env var required")
    size = f"{sample['width']}*{sample['height']}"
    payload = {
        "model": QWEN_MODEL,
        "input": {
            "messages": [{"role": "user", "content": [{"text": sample["prompt"]}]}]
        },
        "parameters": {"size": size, "n": 1},
    }
    req = urllib.request.Request(
        QWEN_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    print(f"[info] qwen size={size}, prompt {len(sample['prompt'])} chars",
          file=sys.stderr)
    resp = _urlopen(req)
    data = json.loads(resp.read())
    url = data["output"]["choices"][0]["message"]["content"][0]["image"]
    urllib.request.urlretrieve(url, out_path)
    print(f"[ok] saved -> {out_path}")


def gen_sensenova(sample, out_path):
    api_key = os.environ.get("SENSENOVA_KEY")
    if not api_key:
        sys.exit("[err] SENSENOVA_KEY env var required")
    size = f"{sample['width']}x{sample['height']}"  # sensenova 用 x
    endpoint = resolve_sensenova_endpoint()
    payload = {
        "model": SENSENOVA_MODEL,
        "prompt": sample["prompt"],
        "size": size,
        "n": 1,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    print(f"[info] sensenova size={size}, prompt {len(sample['prompt'])} chars",
          file=sys.stderr)
    resp = _urlopen(req)
    data = json.loads(resp.read())
    item = (data.get("data") or [None])[0]
    if not item:
        sys.exit(f"[err] empty data: {json.dumps(data)[:500]}")
    if "b64_json" in item:
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(item["b64_json"]))
    elif "url" in item:
        urllib.request.urlretrieve(item["url"], out_path)
    else:
        sys.exit(f"[err] no url/b64: keys={list(item.keys())}")
    print(f"[ok] saved -> {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("index", type=int, help="0-based sample index")
    ap.add_argument("out_path")
    ap.add_argument("--provider", choices=["qwen", "sensenova"], default="qwen")
    args = ap.parse_args()

    sample = load_sample(args.index)
    print(f"[info] sample[{args.index}] {sample['width']}x{sample['height']}",
          file=sys.stderr)
    print(f"[info] first 120 chars: {sample['prompt'][:120]!r}", file=sys.stderr)
    out_dir = os.path.dirname(os.path.abspath(args.out_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    if args.provider == "qwen":
        gen_qwen(sample, args.out_path)
    else:
        gen_sensenova(sample, args.out_path)


if __name__ == "__main__":
    main()
