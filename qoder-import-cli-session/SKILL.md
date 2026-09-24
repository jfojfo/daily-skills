---
name: qoder-import-cli-session
description: 让终端 qodercli 跑的会话出现在 Qoder 桌面 App 侧栏——向 App 主库 chat_sessions 插一行注册记录，App 打开该会话时会自己扫 ~/.qoder/projects 的 JSONL 并把全部消息投影成 source='cli-import'。当用户说"终端起的 session 怎么在 Qoder App 里看""cli 的对话能不能导入桌面端""侧栏看不到 qodercli 的会话""把这条命令行会话搬到 App 里"，或追问 Qoder App 与 qodercli 会话为什么不互通、能不能导入历史会话时使用。
---

# 让终端 qodercli 会话出现在 Qoder 桌面 App 侧栏

范围只有一件事：把一条已存在的终端会话注册进 Qoder 桌面 App，使它在侧栏可见可读。不改写 transcript 内容，不做跨机器搬运，也不负责在 App 里继续对话（见下方"只看不聊"）。

## 为什么会互通、又为什么不互通

Qoder 桌面 App 和 qodercli **共用同一份 transcript 目录**（`~/.qoder/projects/<projectKey>/<sessionId>.jsonl`），但 App 侧栏只列自己主库 `chat_sessions` 里注册过的行。终端起的会话没注册，所以看不见——不是格式问题，纯粹是少一行注册记录。App 也没有任何"扫描收养孤儿 transcript"的逻辑（实测：9 月 2 日就存在的孤儿 transcript，在 App 反复重启后仍未出现在库里）。

App 打开会话时的判定链（读 `app.asar` 得到）：

```
h = !hasMessages(sessionId) || needsCliProjectionRefresh(sessionId)
if (h && supports(descriptor,'history')) l = await readHistory({sessionId, cwd})
   → localPersistence.readMessages(sessionId, cwd)   // 扫 ~/.qoder/projects/*/<sessionId>.jsonl
   → replaceCliImportedMessages(...)                 // 以 source='cli-import' 写进 chat_session_messages
```

两个关键点决定了"只需插一行"：

1. 扫描是**跨 projectKey** 的，只按 `<sessionId>.jsonl` 找文件，不需要猜目录名。
2. 触发条件只有"库里没消息"。终端会话在 App 库里既没有行也没有消息，插一行正好落进这个分支。

`chat_sessions` 上没有 INSERT 触发器（只有 `chat_session_messages` 的 revision 触发器），所以插这一行是惰性的，不会连带改别的表。

## 硬门槛（脚本自己检查，被挡住就别绕）

- **App 必须完全退出**，且 `main.sqlite-wal` / `-shm` 都不存在。有 -wal 说明别的连接活着，那时写库最容易出事。
- **源终端会话必须已退出**：transcript 180 秒内被写过、或有进程 `qodercli -r <SID>` 在跑，就中止。两边同时写一份 JSONL 会互相覆盖。
- **同 cwd 在 App 里至少要有一条现存会话**，否则抄不到 `workspace_id`（`workspaces` 表得有真正对应该目录的行）。让用户先在 App 里对这个目录开一条普通会话，再来 adopt。
- 只写 `chat_sessions` 一张表、只插一行，`changes()` 不等于 1 就回滚退出。

## 操作

`SID` 换成目标会话 id（`qodercli --list-sessions`，或看 `~/.qoder/projects/<key>/` 下的文件名）。

```bash
S=~/work/skills/qoder-import-cli-session/scripts/qoder_adopt.py
python3 $S status  --session-id $SID   # 只读、零副作用：看门槛过不过
python3 $S adopt   --session-id $SID   # 备份 + 插一行（要求 App 已完全退出）
# 用户：启动 Qoder App → 进对应工作区 → 侧栏找到它并点开（点开才触发投影）
python3 $S verify  --session-id $SID   # 确认 cli-import 消息投影出来了
python3 $S rollback --session-id $SID  # 不满意就删掉这一行
```

`adopt` 自动取 transcript 里最后一条 `ai-title`/`custom-title` 当侧栏标题（可 `--title` 覆盖）、用 `state.json` 的 `createdAt`/`updatedAt` 当时间戳、从同 cwd 的现成行抄 `workspace_id`/`execution_target_json`/`model`/`permission_mode`，并把 `main.sqlite` 和该 `.jsonl` 各备份一份到 `/tmp`（备份路径会打印，`integrity_check` 不为 `ok` 就直接中止）。

实测成功判据（真机一条 5.0 MB 会话，插行后在 App 里点开）：

```
messages        {'cli-import': 298, 'sdk-projection': 3}     ← 从 0 涨到这个量级
search_segments 213     history_revision 316
extra_json      {"cliSessionReady":true}                      ← App 自己把 false 翻成 true
title           Verify GPU render output                      ← 沿用 transcript 的 ai-title
```

## 关键陷阱

- **只看不聊**。App 内置 CLI 常比生成 transcript 的 CLI 旧（实测 1.1.57 vs 终端 1.1.61），在 App 里给它发消息等于让旧运行时续写新记录。要继续干活就回终端 `-r <SID>`。
- **App 会回写 JSONL**：改标题、打 tag 会往源 transcript 追加 `{type:"custom-title"}` / `{type:"tag"}`；实测 App 打开后文件从 5,003,279 B 涨到 5,048,177 B（+45 KB）。格式是 CLI 自己在用的，但确实动了原始文件——所以 `adopt` 一定先备份 JSONL。
- **别点自己当前所在的那条会话**：如果这段对话本身是 App 名下、被你在终端 `-r` 接管的，App 重启后再把它拉起来会和终端进程抢同一份 transcript 双写。
- **只读打开 WAL 库会 `SQLITE_CANTOPEN`**：App 退出后没有 -shm，普通 `mode=ro` 打不开，要用 `immutable=1`；反过来 App 正在跑时必须用 `mode=ro` 才看得见 WAL 里没 checkpoint 的新行。脚本按 -wal/-shm 是否存在自动选。
- **`verify` 在沙箱副本上一定返回"没有 cli-import"**：投影是真 App 点开会话时才发生的，副本没有 App 会去读它。沙箱只能验证门槛、行数变化和回滚。
- 不受支持：App 升级或 schema 迁移后这行没人保证兼容，升级后先 `status` 再决定要不要重做。最坏结果是侧栏多一条空白会话，`rollback` 删行即可。

## 回滚

```bash
python3 $S rollback --session-id $SID     # 需要先退出 App
```

整库恢复：退出 App → 删掉 `main.sqlite-wal`/`-shm` → 把 `adopt` 打印的 `/tmp/qoder-main-backup-*.sqlite` 覆盖回 `main.sqlite`。

## 版本兼容

实测环境：Qoder.app 0.3.4（`com.qoder.app.stable`）+ qodercli 1.1.61。表结构、列清单、投影触发条件都可能随版本变。怀疑失效时按 `references/mechanism.md` 末尾的取证命令重查，锚点是 `cli-import`、`needsCliProjectionRefresh`、`replaceCliImportedMessages`；那里还有字段取值的完整清单和表地图。
