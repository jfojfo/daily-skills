---
name: cli-dispatch
description: Dispatch tasks to Codex CLI (codex exec), Qoder CLI (qodercli -p), Claude Code (claude -p), Kimi Code (kimi -p), or Qwen Code (qwen -p) non-interactively with task-level-based model, reasoning effort, and sandbox/permission selection, then parse results from JSONL event streams or structured JSON output. Use when the user wants to delegate a task to codex, qodercli, claude code, kimi, or qwen, run codex exec, qodercli, claude, kimi, or qwen in print mode, dispatch AI coding tasks with different priority/complexity levels, or capture CLI agent execution results programmatically. Trigger terms: codex, codex exec, qodercli, qoder cli, claude, claude code, claude -p, kimi, kimi code, qwen, qwen code, qwen -p, 派发任务, 任务派发, 调用codex, 调用qodercli, 调用claude, 调用kimi, 调用qwen, dispatch to codex, dispatch to qodercli, dispatch to claude, dispatch to kimi, dispatch to qwen.
---

# CLI Task Dispatch

Dispatch tasks to a CLI coding agent non-interactively, select parameters by task level, and parse execution results. Five backends, verified against codex-cli v0.144.5, qodercli v1.1.1, Claude Code v2.1.220, Kimi Code v0.36.1, and Qwen Code v0.21.12.

## Choosing a Backend

- User mentions `codex` / `codex exec` → Codex CLI
- User mentions `qodercli` / `qoder cli` → Qoder CLI
- User mentions `claude` / `claude code` / `claude -p` → Claude Code
- User mentions `kimi` / `kimi code` / `kimi -p` → Kimi Code
- User mentions `qwen` / `qwen code` / `qwen -p` → Qwen Code
- Neither → ask once which CLI to use

## Common Workflow

1. Pick the backend (see above)
2. Classify the task into a level (or ask the user if ambiguous): `light` / `medium` / `heavy`
3. Assemble the command from the backend's parameter table below
4. Run it and capture the result (see each backend's "results" section)
5. Summarize the outcome and ALWAYS report the session id (Codex: `thread_id`; Qoder CLI: `session_id`; Claude Code: `session_id`; Kimi Code: `session_id`; Qwen Code: `session_id`) so the user can resume later

Multiple dispatches are independent sessions and safe to run concurrently (e.g. via background shells). Use distinct output files per task and record each task's session id so any of them can be resumed individually.

## Codex CLI (`codex exec`)

Dispatch via `codex exec` (non-interactive). Defaults: reasoning effort `xhigh`; sessions are persistent (no `--ephemeral`) so every dispatch can be resumed later; network access and web search enabled (Level 1 permissions) so results approach Codex Desktop quality.

### Task Level → Parameters

| Level | Reasoning Effort | Sandbox | Extra Flags | Typical Tasks |
|---|---|---|---|---|
| `light` | `xhigh` (default) | `read-only` | — | Q&A, code reading, quick analysis |
| `medium` | `xhigh` (default) | `workspace-write` + network | — | Small edits, single-file fixes, doc generation |
| `heavy` | `xhigh` (default) | `workspace-write` + network | `--json` (monitor progress) | Multi-file refactors, complex debugging, feature implementation |

- Model: omit `-m` to use the user's config default (`~/.codex/config.toml`). Only pass `-m <MODEL>` when the user explicitly requests a model.
- Reasoning effort defaults to `xhigh` for all levels. Only lower it (`low` / `medium` / `high`; some environments also enable `ultra` / `max`) when the user explicitly asks for a faster/cheaper run.
- Reasoning effort has NO dedicated flag; always pass via `-c model_reasoning_effort="<level>"`.
- Sessions persist by default — do NOT pass `--ephemeral` unless the user explicitly asks for a throwaway run.
- Always add `--skip-git-repo-check`. Add `-C <DIR>` to target a specific working directory.

### Permission Levels

Note: in `codex exec` the approval policy is always `never` (non-interactive, nobody to ask) — what actually gates the agent is the sandbox. Escalate stepwise:

**Level 1 (DEFAULT for medium/heavy)** — workspace write + network + web search. Solves most "failed due to missing permission" quality degradation (npm install, curl, doc lookup):
```
-s workspace-write -c sandbox_workspace_write.network_access=true -c tools.web_search=true
```

**Level 2 (on demand)** — no filesystem/network restrictions, sandbox mechanism still active:
```
-s danger-full-access
```
Use ONLY when the task genuinely needs to touch paths outside the workspace or perform system-level operations (global installs, service management, editing files in $HOME). Confirm with the user before escalating; state why Level 1 is insufficient.

**Never use** `--dangerously-bypass-approvals-and-sandbox` on a local machine — it is intended solely for externally sandboxed environments (CI containers, isolated VMs).

### Command Templates

`tools.web_search=true` is included at every level (it is a model-side tool, independent of sandbox).

**light:**
```bash
codex exec --skip-git-repo-check -s read-only \
  -c model_reasoning_effort="xhigh" -c tools.web_search=true \
  -o /tmp/codex_out.txt "TASK" 2>/dev/null
```

**medium (Level 1 permissions):**
```bash
codex exec --skip-git-repo-check -s workspace-write -C "$WORKDIR" \
  -c sandbox_workspace_write.network_access=true -c tools.web_search=true \
  -c model_reasoning_effort="xhigh" \
  -o /tmp/codex_out.txt "TASK" 2>/dev/null
```

**heavy (Level 1 permissions, JSONL event stream):**
```bash
codex exec --skip-git-repo-check -s workspace-write -C "$WORKDIR" \
  -c sandbox_workspace_write.network_access=true -c tools.web_search=true \
  -c model_reasoning_effort="xhigh" \
  --json "TASK" 2>/dev/null | python3 scripts/parse_events.py
```

**Level 2 escalation (any level, only after user confirms):** replace the `-s ... -c sandbox_workspace_write.network_access=true` portion with `-s danger-full-access`.

Append `2>/dev/null` to suppress thinking tokens on stderr; only show stderr when debugging.

### Getting Results

Three mechanisms, pick by consumer:

1. **`-o <FILE>`** — final agent message written to file. Simplest; use for light/medium. To also capture the session id, add `--json` and parse, or read the `session id:` line printed in the exec header on stdout.
2. **`--json`** — JSONL events on stdout. Use for heavy tasks or when token usage / progress matters. Key events:
   - `{"type":"thread.started","thread_id":"..."}` — session id for resume
   - `{"type":"item.completed","item":{"type":"agent_message","text":"..."}}` — final answer
   - `{"type":"turn.completed","usage":{...}}` — token usage

   Parse with `scripts/parse_events.py` (reads stdin or file, outputs compact JSON: `session_id`, `answer`, `usage`, `errors`).
3. **`--output-schema <FILE>`** — final answer strictly conforms to a JSON Schema. Combine with `-o result.json` for machine-consumable pipelines. Schema must be a valid JSON Schema object with `additionalProperties: false`.

Exit code is 0 on success — use it for orchestration decisions.

### Resuming a Session

```bash
echo "follow-up prompt" | codex exec --skip-git-repo-check resume --last 2>/dev/null
# or by id:
echo "follow-up prompt" | codex exec --skip-git-repo-check resume <THREAD_ID> 2>/dev/null
```

Flags must go between `exec` and `resume`. Do not re-pass model/effort flags on resume unless the user asks to change them.

Since sessions persist by default, prefer resuming an existing session for follow-up work on the same task instead of starting a new dispatch — the session keeps full context.

## Qoder CLI (`qodercli -p`)

Dispatch via print mode and capture results programmatically.

### Quick Start

```bash
qodercli -p --no-session-persistence -o json "your task description"
```

### Task-Level Parameter Matrix

| Level | Model | Reasoning | Permission | Output |
|---|---|---|---|---|
| Light / read-only (query, analyze) | `-m Lite` or `-m Efficient` | (default) | (default) | `-o json` |
| Medium (fix bug, edit files) | `-m Qwen3.7-Max` or `-m Performance` | `--reasoning-effort medium` | `--permission-mode accept_edits` | `-o json` |
| Heavy (refactor, multi-file) | `-m Ultimate` | `--reasoning-effort high` | `--permission-mode bypass_permissions` | `-o stream-json` |

List available models: `qodercli --list-models` (Auto, Ultimate, Performance, Efficient, Lite, Qwen3.8-Max-Preview, Qwen3.7-Max, Kimi-K3, GLM-5.2, DeepSeek-V4-Pro, etc.)

### Key Parameters

- `-p` — non-interactive print mode (required for dispatch); add `--no-session-persistence` for one-shot tasks that need no resume
- `-m <model>` — model name (or modelID for custom models)
- `--reasoning-effort <level>` — thinking level; **invalid values are silently accepted**, so validate before passing
- `--permission-mode <mode>` — `default` / `accept_edits` / `bypass_permissions` / `dont_ask` / `auto`
- `--dangerously-skip-permissions` — bypass all permission checks (equivalent to full-access)
- `-w <dir>` — working directory for the dispatched task
- `--tools` / `--allowed-tools` / `--disallowed-tools` — restrict the sub-task's tool surface
- `--system-prompt` / `--append-system-prompt` — customize the sub-task role
- `--max-output-tokens <n>` — cap output cost
- `--session-id <id>` / `-r <id>` — pin or resume a session for follow-up dispatches

### CRITICAL: Write Tasks Need bypass_permissions

In `-p` mode there is no interactive permission handler. Under `default` mode, all write operations are **silently blocked** — the model replies "tool was blocked" but `is_error` stays `false`. For any task that creates/edits files or runs mutating commands:

```bash
qodercli -p --permission-mode bypass_permissions -o json "create/edit ... task"
```

Do not judge success from `is_error` alone; verify the actual side effect (e.g. the file exists) or check `result` text for "blocked".

### Result Parsing

**`-o json` (recommended for programmatic use)** — single-line JSON object on stdout (hooks do not pollute stdout; safe to pipe):

```json
{"type":"result","subtype":"success","is_error":false,"num_turns":2,
 "result":"final answer text","permission_denials":[],
 "session_id":"...","duration_ms":11596,"usage":{...}}
```

Key fields: `result` (final answer), `is_error`, `num_turns`, `permission_denials`, `session_id` (for `-r` resume), `duration_ms`.

Extract the final answer:
```bash
qodercli -p -o json "task" | tail -1 | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d['result'])"
```

**`-o stream-json` (JSONL event stream)** — one JSON object per line, for real-time monitoring:
- `{"type":"system","subtype":"hook_started|hook_response|init",...}` — startup events; `init` lists tools/model/permissionMode
- `{"type":"assistant","message":{...,"content":[{"type":"text","text":"..."}]}}` — assistant messages
- `{"type":"result","subtype":"success",...}` — final line, same schema as `-o json`

Parse pattern: filter lines by `type`, take the last `result` line for the outcome. `scripts/parse_events.py` handles this automatically (same output schema as the Codex stream).

**`-o text`** — plain final answer only; for simple human-readable dispatch.

### Dispatch Examples

```bash
# Light: cheap model, read-only analysis
qodercli -p -m Lite -o json -w /path/to/repo "分析该目录结构并总结模块职责"

# Medium: balanced model, allow edits
qodercli -p -m Qwen3.7-Max --reasoning-effort medium \
  --permission-mode accept_edits -o json "修复 src/foo.py 中的空指针问题"

# Heavy: flagship model, high reasoning, full write access, streamed events
qodercli -p -m Ultimate --reasoning-effort high \
  --permission-mode bypass_permissions -o stream-json "重构 auth 模块并补充单测"

# Follow-up in the same session
SID=$(qodercli -p -o json "task step 1" | tail -1 | python3 -c "import json,sys; print(json.load(sys.stdin)['session_id'])")
qodercli -p -r "$SID" -o json "continue with step 2"
```

## Claude Code (`claude -p`)

Dispatch via print mode (`-p` / `--print`) and capture results programmatically. Verified against Claude Code v2.1.220. Sessions persist by default (unless `--no-session-persistence`) so every dispatch can be resumed.

### Quick Start

```bash
claude -p --output-format json "your task description"
# or via stdin (safer when the prompt contains shell metacharacters):
printf '%s' "$TASK" | claude -p --output-format json
```

### Task-Level Parameter Matrix

| Level | Model (`--model`) | Effort (`--effort`) | Permission mode | Output format | Typical Tasks |
|---|---|---|---|---|---|
| `light` (read-only, query, analyze) | alias omit / `sonnet` | `medium` | `plan` | `--output-format json` | Q&A, code reading, quick analysis |
| `medium` (fix bug, edit files) | `sonnet` / `opus` | `high` | `acceptEdits` | `--output-format json` | Small edits, single-file fixes, doc generation |
| `heavy` (refactor, multi-file) | `opus` / `fable` | `xhigh` / `max` | `bypassPermissions` | `--output-format stream-json` | Multi-file refactors, complex debugging, feature implementation |

Model aliases: `fable`, `opus`, `sonnet`, `haiku` (map to the latest of each family), or a full model id like `claude-fable-5`. Omit `--model` to use the user's config default. Pass `--effort <level>` for reasoning effort; values: `low` / `medium` / `high` / `xhigh` / `max` — this is Claude Code's analogue of reasoning effort and is independent of the model.

### Key Parameters

- `-p`, `--print` — non-interactive print mode (required for dispatch); add `--no-session-persistence` for one-shot tasks that need no resume
- `--model <model>` / `-m` via alias-less form — model alias (`opus`, `sonnet`, ...) or full id (`claude-fable-5`)
- `--effort <level>` — reasoning effort: `low` / `medium` / `high` / `xhigh` / `max`
- `--permission-mode <mode>` — `default` (=`manual`) / `acceptEdits` / `auto` / `bypassPermissions` / `dontAsk` / `plan`
- `-d` / `--add-dir <dirs...>` — extra directories the agent may access; for the working directory itself just `cd` first (there is no `-C`/`-w` flag — Claude Code runs in the current cwd)
- `--allowed-tools <tools...>` / `--disallowed-tools <tools...>` — restrict tool surface (e.g. `"Bash(git *)" "Edit" "Read"`)
- `--tools <tools...>` — restrict to a specific built-in set; `--tools ""` disables all tools
- `--system-prompt <text>` / `--append-system-prompt <text>` — replace or extend the system prompt
- `--max-budget-usd <amount>` — cap API spend (only works with `-p`)
- `--mcp-config <files...>` / `--settings <file|json>` — bring your own MCP servers / settings
- `--agents <json>` — define custom agents inline (JSON object)
- `--fork-session` — when resuming, create a fresh session id instead of reusing the original

### CRITICAL: Write Tasks Need edit/write Permission + Non-Plan Mode

In `-p` mode there is no interactive permission handler. Under `plan` permission mode the agent can only plan, not apply edits; under `default`/`manual` any write tool call blocks and silently degrades (the agent reports it couldn't make the change). For any task that creates/edits files or runs mutating commands, switch to a write-allowing mode:

```bash
claude -p --permission-mode acceptEdits --output-format json "create/edit ... task"
# full access (sandboxed machines / trusted dirs only):
claude -p --dangerously-skip-permissions --output-format json "..."
```

`--dangerously-skip-permissions` bypasses all checks equivalently to `--permission-mode bypassPermissions` but is the documented "no internet" sandbox escape hatch — prefer `--permission-mode acceptEdits` for ordinary edit tasks and escalate to `bypassPermissions` only when system-level / out-of-workspace operations are required (confirm with the user first).

### Result Parsing

**`--output-format json` (recommended for programmatic use)** — a single JSON object on stdout. Real example:

```json
{"is_error":false,"num_turns":1,"subtype":"success","terminal_reason":"completed",
 "result":"final answer text","session_id":"fee9c09f-...","total_cost_usd":0.0123,
 "usage":{"input_tokens":25184,"output_tokens":3,"cache_read_input_tokens":320,...},
 "modelUsage":{"glm-5.2":{"inputTokens":25184,"...",  "costUSD":0.0123}},
 "permission_denials":[],"type":"result","duration_ms":56695,"uuid":"4f9a4fc0-..."}
```

Key fields: `result` (final answer), `is_error`, `subtype` (`success`/`error_max_turns`/...), `num_turns`, `session_id` (reuse with `-r`), `total_cost_usd`, `usage`, `permission_denials`, `terminal_reason`.

Extract the final answer:
```bash
claude -p --output-format json "task" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d['result']); import sys; sys.exit(1 if d['is_error'] else 0)"
```

**`--output-format stream-json` (JSONL event stream)** — one JSON object per line, for real-time monitoring. Add `--include-partial-messages` to see incremental chunks and `--include-hook-events` for hook lifecycle. Key events:
- `{"type":"system","subtype":"init",...}` — startup; lists tools, model, permissionMode
- `{"type":"assistant","subtype":"text","..."}, {"type":"tool_use",...}, {"type":"user",...}` — turn events
- `{"type":"result","subtype":"success",...}` — final line, same schema as `--output-format json`

Filter lines by `type`, take the last `type=="result"` line for the outcome. `scripts/parse_events.py` does this automatically (same output schema: `session_id`, `answer`, `usage`, `errors`, `success`).

**`--output-format text` (default)** — plain final answer only; for simple human-readable dispatch.

If you want the final answer to strictly conform to a JSON Schema (the analogue of codex's `--output-schema`), pass `--json-schema '<JSON Schema object>'` together with `--output-format json`. The validated object lands in `result`.

### Dispatch Examples

```bash
# Light: cheap model, plan-only analysis (no edits)
claude -p --model sonnet --effort medium --permission-mode plan \
  --output-format json "分析该目录结构并总结模块职责"

# Medium: balanced model, allow edits
claude -p --model opus --effort high --permission-mode acceptEdits \
  --output-format json "修复 src/foo.py 中的空指针问题"

# Heavy: flagship model, full write access, streamed events
claude -p --model fable --effort max --permission-mode bypassPermissions \
  --output-format stream-json "重构 auth 模块并补充单测"

# Follow-up in the same session (sessions persist by default)
SID=$(claude -p --output-format json "task step 1" | python3 -c "import json,sys; print(json.load(sys.stdin)['session_id'])")
claude -p -r "$SID" --output-format json "continue with step 2"
```

### Resuming a Session

```bash
# resume the most recent conversation in the current directory
claude -p -c "follow-up prompt" --output-format json
# or resume a specific session by id
claude -p -r <SESSION_ID> "follow-up prompt" --output-format json
```

`-c`/`--continue` resumes the most recent session in the cwd; `-r`/`--resume <SESSION_ID>` resumes a specific one (the `session_id` field from a prior `result` object). Add `--fork-session` to resume into a fresh session id rather than mutating the original. Prefer resuming an existing session for follow-up work on the same task instead of starting a new dispatch — the session keeps full context.

## Kimi Code (`kimi -p`)

Dispatch via prompt mode (`-p` / `--prompt`) and capture results programmatically. Verified against Kimi Code v0.36.1. The stream event schema is Kimi-specific (`{"role":"...","type":"..."}`), NOT the common `{"type":"result",...}` shape the other three backends share — see "Gotcha" below.

### Quick Start

```bash
kimi -p "your task description" --output-format stream-json
# or, for a plain human-readable final answer:
kimi -p "your task description"
```

### Task-Level Parameter Matrix

| Level | Model (`-m`) | Permission | Output format | Typical Tasks |
|---|---|---|---|---|
| `light` (read-only, query, analyze) | omit (use config default) | `--plan` | `text` | Q&A, code reading, quick analysis |
| `medium` (fix bug, edit files) | omit (use config default) | `--yolo` | `stream-json` | Small edits, single-file fixes, doc generation |
| `heavy` (refactor, multi-file) | omit (use config default) | `--auto` | `stream-json` | Multi-file refactors, complex debugging, feature implementation |

`-m <alias>` resolves a model alias from `~/.kimi-code/config.toml` (`[models.<alias>]` → `[models.<alias>] model = ...`); omit to use config `default_model`. Aliases are user-defined (e.g. `glm-5.2`, `claude-opus-4-8`), not a fixed list — inspect the config or run `kimi provider list` to see what is available.

### Key Parameters

- `-p`, `--prompt <text>` — single non-interactive prompt, print the response and exit (required for dispatch)
- `-m <model>` — model alias from config; omit for `default_model`
- `--output-format <format>` — `text` (default) or `stream-json` (only valid values)
- `-y`, `--yolo` — auto-approve routine tool calls; the agent may still ask questions (NOT fully autonomous)
- `--auto` — fully autonomous mode: no questions, full write access (the heavy/write-task equivalent of `bypass_permissions`)
- `--plan` — start in plan-only mode (read-only, no edits)
- `--add-dir <dir>` — additional workspace directory (repeatable); there is no separate working-directory flag — `cd` first
- `--agent <name>` / `--agent-file <path>` — start with a custom agent profile
- `--skills-dir <dir>` — load skills from a specific dir instead of auto-discovery (repeatable)
- `-S <id>`, `--session [id]` — resume a session by id (no id → interactive picker, but in `-p` mode always pass the id); cannot combine with `--agent`/`--agent-file`
- `-c`, `--continue` — continue the most recent session for the current working directory

### CRITICAL: Write Tasks Need `--yolo` or `--auto`

`-p` mode has no interactive handler. In `--plan` mode the agent can only read/plan; a plain `kimi -p` (default permissions) blocks writes and silently degrades. For any edit/create task:

```bash
# routine edits, agent may still ask questions:
kimi -p "fix the bug in src/foo.py" --yolo
# fully autonomous, multi-file / scripted:
kimi -p "refactor the auth module and add unit tests" --auto
```

`--auto` is the write-access escape hatch (equivalent of `bypass_permissions`); `--yolo` is the lighter touch that still pauses for genuine questions. Verify the actual side effect (file exists) rather than trusting the response text alone — a blocked write can still return an answer claiming it could not make the change.

### Result Parsing

**`--output-format stream-json` (recommended for programmatic use)** — one JSON object per line on stdout, Kimi-specific roles/types. Real example:

```json
{"role":"meta","type":"system.version","version":"0.36.1"}
{"role":"assistant","content":"hi"}
{"role":"meta","type":"session.resume_hint","session_id":"session_3611d976-...","command":"kimi -r session_3611d976-...","content":"To resume this session: kimi -r session_3611d976-..."}
```

Key messages:
- `{"role":"meta","type":"system.version",...}` — startup/version marker
- `{"role":"assistant","content":"..."}` — the agent's answer (last one wins; take the final `assistant` message)
- `{"role":"meta","type":"session.resume_hint","session_id":"...","command":"..."}` — carries the `session_id` for resume

Note the `command:` field prints `kimi -r <id>` as a convenience, but the actual resume flag is `-S`/`--session` (the `-r` shown there is a migration/back-compat hint) — see "Resuming" below. `scripts/parse_events.py` handles this stream automatically and surfaces `session_id` + `answer`.

There is no single `{"type":"result",...}` line with `is_error`/`usage` aggregated — exit code is the success signal. If you need token usage, it is generally not exposed in `stream-json`; rely on `kimi provider list` / provider dashboards instead.

Extract the final answer:
```bash
kimi -p "task" --output-format stream-json | python3 -c \
  "import json,sys
ans=None; sid=None
for line in sys.stdin:
  try: e=json.loads(line)
  except: continue
  if e.get('role')=='assistant': ans=e.get('content')
  elif e.get('role')=='meta' and e.get('type')=='session.resume_hint': sid=e.get('session_id')
print(ans or '')"
```

**`--output-format text` (default)** — plain final answer, e.g. `` `• hi` ``. Simplest for human-readable dispatch (note the leading bullet/decoration prefix when parsing; strip non-content lines if needed).

### Dispatch Examples

```bash
# Light: default model, plan-only analysis (no edits)
kimi -p "分析该目录结构并总结模块职责" --plan

# Medium: allow edits (yolo), capture structured stream
kimi -p "修复 src/foo.py 中的空指针问题" --yolo --output-format stream-json

# Heavy: flagship model, fully autonomous
kimi -p "重构 auth 模块并补充单测" --auto --output-format stream-json

# Follow-up in the same session (sessions persist)
SID=$(kimi -p "task step 1" --output-format stream-json | python3 -c \
  "import json,sys
sid=None
for line in sys.stdin:
  try: e=json.loads(line)
  except: continue
  if e.get('role')=='meta' and e.get('type')=='session.resume_hint': sid=e.get('session_id')
print(sid)")
kimi -p -S "$SID" "continue with step 2" --output-format stream-json
```

### Resuming a Session

```bash
# resume the most recent session for the current working directory
kimi -p -c "follow-up prompt" --output-format stream-json
# resume a specific session by id
kimi -p -S <SESSION_ID> "follow-up prompt" --output-format stream-json
```

`-c` reads the last session for the cwd; `-S <id>` resumes a specific one (the `session_id` from a prior `session.resume_hint` message). IMPORTANT: even though the resume_hint prints `kimi -r <id>`, the real resume flag is `-S`, not `-r`; `-r` as a positional id is rejected as an unknown command. Put `-S <id>` on the flags side of the command and pass the prompt via `-p "<text>"` (positional args are not reliably accepted alongside `-S`). Prefer resuming for follow-up work on the same task — the session keeps full context.

## Qwen Code (`qwen -p`)

Dispatch via `qwen -p` (non-interactive prompt mode) and capture results programmatically. Verified against Qwen Code v0.21.12. The result schema is the common `{"type":"result",...}` shape shared by codex/qoder/claude — `scripts/parse_events.py` handles it unchanged.

### Quick Start

```bash
qwen -p "your task description" -o json
# stdin content is appended to the prompt (combine with -p for large prompts):
printf '%s' "$TASK" | qwen -p "" -o json
```

### Task-Level Parameter Matrix

| Level | Model (`-m`) | Sandbox | Output format | Typical Tasks |
|---|---|---|---|---|
| `light` (read-only, query, analyze) | omit (config default) | (default) | `-o json` | Q&A, code reading, quick analysis |
| `medium` (fix bug, edit files) | omit (config default) | (default) | `-o json` | Small edits, single-file fixes, doc generation |
| `heavy` (refactor, multi-file) | omit (config default) | `--sandbox` | `-o stream-json` | Multi-file refactors, complex debugging, feature implementation |

`-m <model>` takes a model id/alias from `~/.qwen/settings.json` (`model.name`, plus entries under `modelProviders`); omit to use the config default (e.g. `qwen3.8-max`). `--fallback-model <m>` adds one or more fallbacks (repeatable or comma-separated, max 3) tried when the primary is at capacity.

### Key Parameters

- `-p`, `--prompt <text>` — single non-interactive prompt; stdin content is appended to `-p` (use `-p ""` to feed the whole task via stdin). Required for dispatch.
- `-m`, `--model <model>` — model id/alias from config; omit for the default
- `--fallback-model <model>` — capacity fallback(s), repeatable / comma-separated, max 3
- `-o`, `--output-format <format>` — `text` (default) / `json` / `stream-json`
- `-s`, `--sandbox` — run in a filesystem sandbox (restricts working-directory writes); NOT a permission-mode toggle
- `-i`, `--prompt-interactive <text>` — run the prompt then continue interactively (not for dispatch)
- `--safe-mode` — disable all customizations (context files, hooks, extensions, skills, MCP) for troubleshooting
- `--bare` — minimal mode: skip implicit startup auto-discovery; only honor explicit CLI inputs
- `--proxy <url>` — proxy for Qwen Code (deprecated; prefer the `proxy` setting in settings.json)
- `--insecure` — skip TLS verification (self-signed certs only); see warning in `--help`
- `-r`, `--resume [id]` — resume a specific session by id (no id → picker); the `session_id` from a prior `result` object
- `-c`, `--continue` — resume the most recent session for the current project
- There is NO `--permission-mode`, `--yolo`, `--auto`, `--effort`, `--allowed-tools`, or `-C`/`-w` flag — those don't exist on `qwen` (passing them yields `Unknown arguments`). Permission mode comes from the environment/settings, described below.

### CRITICAL: Permission Mode Is Set in Settings, Not on the CLI

Unlike the other backends, Qwen Code has no CLI flag for permission mode. The active mode is reflected in the `{"type":"system","subtype":"init",...}` event's `permission_mode` field (commonly `auto` when `autoModeAcknowledged: true` is set in `~/.qwen/settings.json`). To run write tasks autonomously in `-p` mode:

1. Confirm/raise the permission mode in `~/.qwen/settings.json` (the `security`/permissions block, `autoModeAcknowledged`, or the project's `.qwen/settings.json`). The runtime default here was `permission_mode: "auto"`.
2. Run `qwen -p "<write task>" -o json` and verify the actual side effect (file changed) — a blocked write still returns a `result` whose text claims it could not make the change.
3. Restrict blast radius for untrusted prompts via `--sandbox` and/or by editing the settings' tool/permission surface, since there is no `--allowed-tools` flag.

`--sandbox` constrains the filesystem, not the approval policy — it does not enable or disable write approval.

### Result Parsing

**`-o json` (recommended for programmatic use)** — a single JSON array on stdout (NOT an object; it is an array of the session's events ending in one `result` entry). Real example (last element):

```json
{"type":"result","subtype":"success","uuid":"...","session_id":"44baea69-...",
 "is_error":false,"duration_ms":588,"num_turns":1,
 "result":"final answer text",
 "usage":{"input_tokens":0,"output_tokens":0,"cache_read_input_tokens":0},
 "permission_denials":[],
 "stats":{"models":{...},"tools":{...},"files":{...},"skills":{...}}}
```

Earlier array elements: `{"type":"system","subtype":"init","tools":[...],"model":"...","permission_mode":"auto",...}` then assistant `{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"..."}],"usage":{...}}}`. The final `result` element carries `result` (answer), `is_error`, `subtype`, `session_id`, `usage`, `permission_denials`, and a richer `stats` block.

Extract the final answer (note: output is a JSON **array**, take the last `result` entry):
```bash
qwen -p "task" -o json | python3 -c \
  "import json,sys;
   d=json.load(sys.stdin);
   r=[x for x in d if x.get('type')=='result'][-1];
   print(r['result']); import sys; sys.exit(1 if r['is_error'] else 0)"
```

**`-o stream-json` (JSONL event stream)** — one JSON object per line, same Common schema as claude/qoder: `system init`, `assistant`, then a final `result`. `scripts/parse_events.py` parses this unchanged — feed the stream, get `{session_id, answer, usage, errors, success}`.

**`-o text` (default)** — plain final answer; for simple human-readable dispatch.

### Dispatch Examples

```bash
# Light: default model, read-only analysis
qwen -p "分析该目录结构并总结模块职责" -o json

# Medium: specify a model, allow edits (ensure permission mode allows writes via settings)
qwen -p "修复 src/foo.py 中的空指针问题" -m glm-5 -o json

# Heavy: flagship model, sandboxed, streamed events
qwen -p "重构 auth 模块并补充单测" -m qwen3.8-max-preview --sandbox -o stream-json

# Follow-up in the same session (sessions persist)
SID=$(qwen -p "task step 1" -o json | python3 -c "import json,sys; d=json.load(sys.stdin); print([x for x in d if x.get('type')=='result'][-1]['session_id'])")
qwen -p -r "$SID" "continue with step 2" -o json
```

### Resuming a Session

```bash
# resume the most recent session for the current project
qwen -p -c "follow-up prompt" -o json
# resume a specific session by id
qwen -p -r <SESSION_ID> "follow-up prompt" -o json
```

`-c` continues the last session tied to the current project; `-r <SESSION_ID>` resumes a specific one (the `session_id` from a prior `result` entry). Prefer resuming for follow-up work on the same task — the session keeps full context.

## Notes

- Long tasks: run in background and poll, or set a generous timeout; heavy tasks routinely exceed 60s on all five CLIs.
- Codex: a stderr warning like `failed to load models cache: missing field ...` is harmless (stale cache after CLI upgrade).
- Codex: a `Skill descriptions were shortened...` item.completed error event is a context-budget warning, not a task failure — `parse_events.py` reports it under `errors` but the answer is still valid.
- Codex: if the prompt contains shell metacharacters, pass it via stdin: `printf '%s' "$TASK" | codex exec ... -`
- Qoder CLI: `--output-format` invalid values fail with usage help (non-zero exit); `--reasoning-effort` invalid values do NOT fail — caller must validate.
- Qoder CLI: restrict `--allowed-tools` for untrusted/dispatched prompts to reduce blast radius when using `bypass_permissions`.
- Claude Code: there is no `-C`/`-w` working-directory flag — `cd` to the target dir first, then use `--add-dir <dir>` to grant access to additional directories. Workspace-trust dialog is auto-skipped in `-p` mode (or when stdout is not a TTY); only run in trusted dirs.
- Claude Code: `--effort` is the analogue of reasoning effort. `--dangerously-skip-permissions` ≈ `--permission-mode bypassPermissions` but is the sandbox/no-internet escape hatch; prefer `acceptEdits` for ordinary edit tasks.
- Claude Code: if the prompt contains shell metacharacters, prefer reading it from stdin (`printf '%s' "$TASK" | claude -p --output-format json`) to avoid quoting bugs.
- Claude Code: judge success from `is_error` + `subtype` (and the actual side effect for write tasks), not from `result` text alone — a blocked permission under a read-only mode can still return a non-error result that says it couldn't make the change.
- Kimi Code: stream event shape is `{"role":"...","type":"..."}` — NOT the common `{"type":"result",...}` used by codex/qoder/claude. The answer is the last `{"role":"assistant","content":"..."}` message; there is no aggregated result object with `is_error`/`usage`. Rely on exit code + side effect for success.
- Kimi Code: the `session.resume_hint` `command` field prints `kimi -r <id>`, but the real resume flag is `-S`/`--session <id>`. Passing `-r <id>` positionally is rejected as `unknown command`. Always resume with `-S <id>` on the flags side.
- Kimi Code: resume sometimes rejects a positional prompt alongside `-S`; pass the follow-up via `-p "<text>"` rather than a bare positional argument.
- Kimi Code: `--output-format` only accepts `text` and `stream-json` — there is no single-line `json` aggregate. Use `stream-json` + `parse_events.py` for machine parsing.
- Qwen Code: auth is read from `~/.qwen/settings.json` (`security.auth`), not just env. If `qwen` reports "未找到 ANTHROPIC_API_KEY", the selected auth type expects that env var / settings key — set `ANTHROPIC_API_KEY` (or the configured `envKey`) in the environment or settings before dispatching.
- Qwen Code: there is NO `--permission-mode` / `--effort` / `--allowed-tools` / `-C`/`-w` flag — these are rejected as `Unknown arguments`. Permission mode lives in settings and is surfaced in the `init` event's `permission_mode`; use `--sandbox` only for filesystem restriction, not approval control.
- Qwen Code: `-o json` emits a JSON **array** of events, not a single object — take the last `{"type":"result",...}` element for the answer/session_id. `-o stream-json` (one object per line) is what `parse_events.py` consumes directly.
- Qwen Code: `permission_denials` errors (e.g. "blocked" / 文档侧 API 4xx during dispatch) still give `is_error: false` with the model's tool-error text in `result` — check `permission_denials` and the side effect, not `is_error` alone.
