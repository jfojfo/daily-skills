#!/usr/bin/env python3
"""Parse CLI agent JSONL event streams
(codex exec --json / qodercli -o stream-json / claude -p --output-format stream-json /
 kimi -p --output-format stream-json / qwen -p -o stream-json).

Reads from stdin or a file argument. Lines may carry an "N:" prefix
(codex numbers its JSONL lines); both prefixed and bare JSON are handled.
Note: qwen's `-o json` emits a single JSON ARRAY (not line-delimited) and must be
expanded to one object per line first (e.g. `jq -c '.[]'`) before piping here;
qwen's `-o stream-json` is line-delimited and can be piped directly.

The stream formats are auto-detected per event type / role:

  codex exec --json      thread.started / item.completed / turn.completed / turn.failed
  qodercli -o stream-json  a final {"type":"result",...} line
  claude -p --output-format stream-json  a final {"type":"result",...} line
  qwen -p -o stream-json  init / assistant / a final {"type":"result",...} line
  kimi -p --output-format stream-json   {"role":"meta","type":"session.resume_hint",...}
                                        + {"role":"assistant","content":"..."} (no result/usage)

Output: one compact JSON object on stdout:
  {
    "session_id": "...",       # session id, usable with
                                #   codex:  `codex exec resume <id>`
                                #   qodercli: `qodercli -p -r <id>`
                                #   claude:  `claude -p -r <id>`
                                #   qwen:    `qwen -p -r <id>`
                                #   kimi:    `kimi -p -S <id>`  (NOT -r)
    "thread_id": "...",        # alias of session_id (kept for codex naming)
    "answer": "...",           # final agent message text (last one wins)
    "usage": {...},            # token usage (codex/qoder/claude/qwen; null for kimi)
    "errors": [...],           # error items (e.g. context-budget warnings)
    "success": true/false      # true if an answer was produced
  }

Exit code: 0 if an answer was found, 1 otherwise.
"""
import json
import re
import sys

LINE_PREFIX = re.compile(r"^\d+:")


def parse_stream(lines):
    result = {"session_id": None, "thread_id": None, "answer": None, "usage": None, "errors": [], "success": False}
    for raw in lines:
        line = LINE_PREFIX.sub("", raw.strip(), count=1)
        if not line or not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        role = event.get("role")
        # Common schema (codex exec --json / qodercli -o stream-json / claude -p --output-format stream-json):
        if etype == "thread.started":
            result["thread_id"] = event.get("thread_id")
        elif etype == "item.completed":
            item = event.get("item", {})
            if item.get("type") == "agent_message":
                result["answer"] = item.get("text")
            elif item.get("type") == "error":
                result["errors"].append(item.get("message"))
        elif etype == "turn.completed":
            result["usage"] = event.get("usage")
        elif etype == "turn.failed":
            result["errors"].append(json.dumps(event.get("error", event), ensure_ascii=False))
        elif etype == "result":
            result["answer"] = event.get("result")
            result["session_id"] = event.get("session_id")
            result["usage"] = event.get("usage")
            if event.get("is_error"):
                result["errors"].append(event.get("result"))
        # Kimi Code stream (kimi -p --output-format stream-json):
        #   {"role":"meta","type":"system.version"/"session.resume_hint",...}
        #   {"role":"assistant","content":"..."}
        elif role == "meta" and etype == "session.resume_hint":
            sid = event.get("session_id")
            if sid:
                result["session_id"] = sid
        elif role == "assistant":
            content = event.get("content")
            if content is not None:
                result["answer"] = content
    if result["session_id"] is None:
        result["session_id"] = result["thread_id"]
    elif result["thread_id"] is None:
        result["thread_id"] = result["session_id"]
    result["success"] = result["answer"] is not None
    return result


def main():
    source = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    try:
        result = parse_stream(source)
    finally:
        if source is not sys.stdin:
            source.close()
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
