[中文](./README.zh.md) · **English**

# daily-skills

My personal Agent Skill repo. Each top-level directory is a self-contained skill — one `SKILL.md` plus its own scripts and resources. Symlink it into your agent's skills directory and the agent discovers it, then loads it when the task calls for it.

No build step, no third-party dependencies: the scripts use only the Python 3 standard library, and credentials are always read from environment variables.

Every skill follows the open [Agent Skills](https://agentskills.io) standard, so any of the 40+ clients that implement it can load them — Claude Code, Codex, Qoder, Kimi Code, CodeBuddy, OpenCode, Cursor and others.

## Skills

| Skill | What it does | Key needed | Docs |
| --- | --- | --- | --- |
| **infographic-gen** | Turns the key points of a doc / SKILL / README into an infographic while preserving the source language. Ships three three-column style templates (cute cartoon, minimal business, tech-dark HUD) plus a library of 100 sample prompts (20+ visual styles, renderable straight from an index). Set the canvas and it makes covers too: WeChat headers, Xiaohongshu covers, music / podcast covers | Choose one: `DASHSCOPE_API_KEY` or `SENSENOVA_API_KEY` | [infographic-gen/SKILL.md](infographic-gen/SKILL.md) |
| **cli-dispatch** | Dispatches tasks to Codex CLI (`codex exec`), Qoder CLI (`qodercli -p`), Claude Code (`claude -p`), Kimi Code (`kimi -p`), or Qwen Code (`qwen -p`) non-interactively: task-level selection of model, reasoning effort and sandbox/permission, unified result parsing, and session resume | — (local CLI login) | [cli-dispatch/SKILL.md](cli-dispatch/SKILL.md) |
| **qoder-import-cli-session** | Makes a terminal `qodercli` session appear in the Qoder desktop sidebar, so you can open and read its history in the app | None. Qoder must be installed locally | [qoder-import-cli-session/SKILL.md](qoder-import-cli-session/SKILL.md) |

## infographic-gen

### How to use it

Install the skill, configure one image service, then give the agent your source material and describe the result you want. Useful details include the audience, where the image will be published, the style, the aspect ratio, and any title that must appear exactly.

- Turn our team wiki's onboarding guide into a cute cartoon infographic.
- Summarize this document as a minimal business infographic for next week's review, in landscape format.
- Make a tech-dark architecture infographic from this gateway design document.
- Use the style of sample 13 from the [sample library](infographic-gen/references/sample-library.md).
- Make another version with sensenova so I can compare them.
- Create a 2.35:1 WeChat header for this article with the title "...".
- Make a 3:4 Xiaohongshu cover with very little text.
- Design a dark, minimal 1:1 album cover for this EP.

You can also name it explicitly: type `$infographic-gen` in Codex, or just say "use infographic-gen" in Claude Code / Qoder.

infographic-gen keeps the source language by default. The agent extracts the main points, generates the image, checks its text and layout, and returns the finished file. Image models can still struggle with dense or exact wording. If every character must be perfect, use an editable design or typesetting workflow instead.

### Built-in templates

The three built-in templates below were rendered with `qwen-image-3.0-pro` from the same source content, making their visual differences easy to compare.

<table>
  <tr>
    <td align="center"><img src="infographic-gen/examples/skill-self-business-qwen.jpg" width="300" alt="Minimal business infographic"><br><sub><b>Minimal business</b></sub></td>
    <td align="center"><img src="infographic-gen/examples/skill-self-cartoon-qwen.jpg" width="300" alt="Cute cartoon infographic"><br><sub><b>Cute cartoon</b></sub></td>
    <td align="center"><img src="infographic-gen/examples/skill-self-tech-dark-qwen.jpg" width="300" alt="Tech-dark HUD infographic"><br><sub><b>Tech-dark HUD</b></sub></td>
  </tr>
</table>

### 15 styles selected from the 100-prompt library

The sample library covers different subjects, languages, aspect ratios, information structures, and visual treatments. These 15 renders provide a quick overview; use the [sample library index](infographic-gen/references/sample-library.md) to browse all 100 prompts.

<table>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-26-comic.jpg" width="240" alt="Comic-book infographic"><br><sub><b>Comic book</b> · #26</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-28-data-chart.jpg" width="240" alt="Data-chart infographic"><br><sub><b>Data chart</b> · #28</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-34-watercolor.jpg" width="240" alt="Watercolor infographic"><br><sub><b>Watercolor</b> · #34</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-35-ar.jpg" width="240" alt="Augmented-reality interface infographic"><br><sub><b>AR interface</b> · #35</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-42-grid.jpg" width="240" alt="Grid-layout infographic"><br><sub><b>Grid</b> · #42</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-45-mechanical.jpg" width="240" alt="Mechanical-style infographic"><br><sub><b>Mechanical</b> · #45</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-51-chinese-ink.jpg" width="240" alt="Chinese ink-style infographic"><br><sub><b>Chinese ink</b> · #51</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-53-blueprint.jpg" width="240" alt="Blueprint collage infographic"><br><sub><b>Blueprint collage</b> · #53</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-54-archival.jpg" width="240" alt="Archival collage infographic"><br><sub><b>Archival</b> · #54</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-56-oil-baroque.jpg" width="240" alt="Oil and Baroque-style infographic"><br><sub><b>Oil / Baroque</b> · #56</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-63-cyberpunk.jpg" width="240" alt="Cyberpunk infographic"><br><sub><b>Cyberpunk</b> · #63</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-64-biomed.jpg" width="240" alt="Biomedical infographic"><br><sub><b>Biomedical</b> · #64</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-67-flat-vibrant.jpg" width="240" alt="Flat vibrant infographic"><br><sub><b>Flat vibrant</b> · #67</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-70-iceberg.jpg" width="240" alt="Iceberg metaphor infographic"><br><sub><b>Iceberg</b> · #70</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-85-chalkboard.jpg" width="240" alt="Chalkboard infographic"><br><sub><b>Chalkboard</b> · #85</sub></td>
  </tr>
</table>

### Cover images

infographic-gen can also make cover images. Tell the agent where the image will be used, the exact title, and the style you want. The agent handles the canvas size, cropping, and export.

| Use | Ratio | Typical final size |
| --- | --- | --- |
| WeChat Official Account header | 2.35:1 | 900 × 383 |
| WeChat image post / Xiaohongshu cover | 3:4 portrait | 1080 × 1440 |
| Music, podcast, or album cover | 1:1 square | 1080 × 1080 |
| Standard infographic | 16:9 landscape | Based on your use |

Covers work best with a short headline. Give the title exactly as it should appear and leave longer explanations in the article or post. Image models can misspell, omit, or repeat text, so the agent should inspect the final image before returning it.

### Choose an image service

infographic-gen supports two image services. Configure one of them:

| Service | Key | When to choose it |
| --- | --- | --- |
| qwen, the default | `DASHSCOPE_API_KEY` | General infographics, especially layouts with more text |
| sensenova | `SENSENOVA_API_KEY` | An alternative when you prefer SenseNova or qwen is unavailable |

Only one key is needed. Save it in your local environment rather than pasting it into a prompt or document. If you have only configured SenseNova, mention sensenova in your request because qwen is the default. Image generation may use paid balance or free quota, so check your account before requesting a large batch.

## cli-dispatch

Delegates a task to a CLI coding agent non-interactively: pick the backend, classify the task as `light` / `medium` / `heavy`, and the skill assembles the command (model, reasoning effort, sandbox / permission mode), runs it, parses the result, and reports a session id for follow-ups.

Trigger examples:

```
Dispatch the auth-module refactor to codex, heavy level
Dispatch this bug fix to qodercli, medium level
Use kimi to analyze the module responsibilities of this directory, read-only
Dispatch to claude and report the session id
Run the same task again on qwen for comparison
Dispatch the code refactor to codex for review — run with danger-full-access, a persistent session, and xhigh reasoning
```

You can also name it explicitly: just say "Use the cli-dispatch skill to dispatch the code refactor to codex for review".

| Backend | Dispatch | Write tasks need | Resume | Verified |
| --- | --- | --- | --- | --- |
| Codex CLI | `codex exec` | sandbox escalation (`-s workspace-write` … `danger-full-access`) | `codex exec resume <id>` | v0.144.5 |
| Qoder CLI | `qodercli -p` | `--permission-mode bypass_permissions` | `-r <id>` | v1.1.1 |
| Claude Code | `claude -p` | `--permission-mode acceptEdits` / `bypassPermissions` | `-r <id>` / `-c` | v2.1.220 |
| Kimi Code | `kimi -p` | `--yolo` / `--auto` | `-S <id>` (not `-r`!) | v0.36.1 |
| Qwen Code | `qwen -p` | permission mode configured in `~/.qwen/settings.json` | `-r <id>` / `-c` | v0.21.12 |

`scripts/parse_events.py` normalizes all five event-stream formats into one JSON object (`session_id`, `answer`, `usage`, `errors`, `success`), so the dispatch side looks the same whichever CLI runs the task — including the odd ones out: qwen's `-o json` emits a JSON array, and kimi's stream has no `result` line at all. Sessions persist by default on every backend, so follow-ups reuse the full context instead of starting over. Requires only that the target CLI is installed and logged in — no API key.

## qoder-import-cli-session

Sessions started with `qodercli` do not normally appear in the Qoder desktop app. This skill imports an existing terminal session into the app sidebar, where you can open it and read the full conversation history.

Ask your agent in plain language:

```
Import this qodercli session into the Qoder desktop app
Import my latest qodercli session into the Qoder app
Make the Qoder session I just used in the terminal appear in the app sidebar
```

The agent will find the session, check that it is safe to import, create backups, and add it to Qoder. When prompted, reopen Qoder and click the imported session once so the app can load its history. The agent can then verify that the import worked.

Before importing, fully quit the Qoder desktop app and stop the source `qodercli` session. The same project folder also needs at least one existing conversation created in the desktop app. If there is none, open that folder in Qoder, start a temporary conversation, then quit the app and ask the agent to import again.

Use the imported session for reading in the desktop app. To continue the conversation, return to the terminal and resume it with `qodercli`. The agent can also undo the import if you no longer want it in the sidebar.

Currently verified with Qoder.app 0.3.4 and qodercli 1.1.61. Ask the agent to check compatibility again after upgrading Qoder.

## Installation

### Option 1: let the agent install it

In Claude Code, Codex or any other tool that supports Agent Skills, just say:

```
Install this skill for me: https://github.com/jfojfo/daily-skills/tree/main/<skill-name>
```

The agent clones it into the right directory itself — you don't have to think about paths.

### Option 2: clone + symlink

Use this if you also want to edit the skill: change it once in the repo and every agent picks it up immediately, no re-copying.

```bash
git clone https://github.com/jfojfo/daily-skills.git
cd daily-skills && REPO=$(pwd)
SKILL=infographic-gen   # infographic-gen, cli-dispatch, qoder-import-cli-session, ...

# Claude Code
ln -s "$REPO/$SKILL" ~/.claude/skills/$SKILL

# Codex
ln -s "$REPO/$SKILL" ~/.codex/skills/$SKILL

# Qoder
ln -s "$REPO/$SKILL" ~/.qoder/skills/$SKILL
```

### Uninstall

Just delete the symlink; the repo is untouched: `rm ~/.claude/skills/<skill-name>`

### If your agent doesn't support skills

Download the full `<skill-name>/SKILL.md`, use it as a project rules file, or simply paste it into the conversation and let the agent follow it. The result is the same — a skill is just a structured set of instructions and needs no runtime.

## License

[MIT](LICENSE), covering this repo's own scripts and documentation.

The 100 sample prompts in `infographic-gen/prompts/samples_infographic.jsonl` were collected from public sources and serve only as visual reference when writing your own prompts; rights to them remain with their original authors.
