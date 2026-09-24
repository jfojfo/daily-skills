# 机制取证：Qoder 桌面 App 与 qodercli 的会话存储关系

实测环境：Qoder.app 0.3.4（bundle id `com.qoder.app`，userData 目录名 `com.qoder.app.stable`）+ qodercli 1.1.61（内置 `qoderCliVersion: 1.1.57`）。所有结论都来自本机文件与 `app.asar` 取证，不是文档转述。

## 目录与库地图

| 位置 | 角色 |
| --- | --- |
| `~/.qoder/projects/<projectKey>/<sessionId>.jsonl` | transcript 真相源，**CLI 和 App 共用**。`projectKey` 是把 cwd 的 `/` 换成 `-`（如 `-Users-jfo-work-agent`） |
| `~/.qoder/projects/<projectKey>/<sessionId>/state.json` | 会话状态：`createdAt`/`updatedAt`/`workspaceDirectories`/`revision` |
| `~/Library/Application Support/com.qoder.app.stable/main.sqlite` | App 私有库：会话注册表 + 投影缓存 + 工作区 + 侧栏分组 |
| `…/chat-session-turn-payload-buffer.sqlite` | 流式 turn 的 payload 缓冲 |
| `…/qoder-data.v1.json` | App 的 runtime 注册表（`runtime:qoder` = Built-in local CLI，`commandName: qodercli`，capabilities 含 `resume`/`fork`） |

## 为什么侧栏看不到终端会话

App 侧栏只查自己的 `chat_sessions`。实测覆盖关系：`~/.qoder/projects/-Users-jfo-work-agent/*.jsonl` 46 个，`chat_sessions` 45 行，交集 43；差的 3 条正是纯终端会话。9 月 2 日就存在的孤儿 transcript 在 App 反复重启后仍未被收养 → **不存在扫描收养逻辑**。

App 是会话的发起方：行由 App `INSERT`，`extra_json` 写 `cliSessionReady`，启动 CLI 时拼 `--session-id <uuid>` / `--resume <id>` / `--continue` / `--fork-session` 等参数（app.asar 里的参数拼装代码）。

数据导入源（`sessionMigrationSources`）只有两个，没有 CLI：

```js
{sourceProduct:"quest",   databaseRelativePaths:[["Qoder","SharedClientCache","cache","db","local.db"]], …}
{sourceProduct:"qoderWork",databaseRelativePaths:[["QoderWork","data","agents.db"]], transcriptRootDirectoryName:".qoderwork"}
```

Deep link 只注册了 `qoder` / `qoder-app` 两个 scheme，处理逻辑里只有 `qoder://settings/<section>` 和 `qoder://invite?token=`，**没有** `qoder://session/<id>`。

## 投影链（本技能立足点）

App 打开会话时的判定，从 app.asar 里定位到的等价逻辑：

```
const g = store.hasMessages(sessionId)
const h = !r && !o && (!g || store.needsCliProjectionRefresh(sessionId))
if (descriptor && executionSessionAccess.supports(descriptor, 'history') && h) {
    l = await executionSessionAccess.readHistory({ location:{route, cwd}, … })
    if (l) store.replaceCliImportedMessages(sessionId, projectStoredConversation(l))
}
```

`readHistory` 最终落到本地适配器：

```
readMessages(sessionId, cwd, {view}) → localPersistence.readMessages(...)
// 内部：for (dir of readdir(~/.qoder/projects)) 若 dir/<sessionId>.jsonl 存在且 size>0 → 读它
```

即 **跨 projectKey 按文件名找**，所以只要 sessionId 对得上就能读到。

`chat_session_messages.source` 的取值：库里原有 `sdk-projection`（App 自己流式落的）、`host-projection`、`fork-inherited`，加上这条链路的 `cli-import`。一条 message = 一轮 user 或一轮 assistant，`payload_json` 里带 `tools[]`（含工具输入与响应文本）。

写入侧还有个副作用：`w()` 里当 `source==='sdk-projection' && role==='assistant' && status in (streaming,completed)` 且有内容时，会把该会话 `extra_json.$.cliSessionReady` 从 0 更新成 true——所以 verify 时看到 true 是 App 干的，不是我们写的。

## 实测数据（一条 5.0 MB 的真终端会话）

插行前：`chat_sessions` 46 行（含本次插入）、该 sessionId 在 `chat_session_messages` 里 0 行。

App 启动并点开该会话后：

```
messages        {'cli-import': 298, 'sdk-projection': 3}     合计 301
search_segments 213
history_revision 316
extra_json      {"cliSessionReady":true}
title           Verify GPU render output        ← 沿用 transcript 里的 ai-title
jsonl           5,003,279 B → 5,048,177 B（App 追加了 ai-title/custom-title/tag 等记录）
```

最小注册行的字段取值（`quote()` 核对过的同 cwd 现存行）：

```
origin_session_id=NULL  session_kind='standard'  conversation_mode='normal'  product_mode='coding'
cwd=<与 transcript 相同的绝对路径>  execution_kind='local'  workspace_id=<workspaces 表里该目录的行>
git_branch=NULL  model='qfmodel'  permission_mode='auto'  additional_direcotries='{}'   ← 列名 App 自己拼错了
extra_json='{"cliSessionReady":false}'  created_at/updated_at=毫秒  execution_target_json=<同 cwd 行>
archived=0  unread=0  deleted_at=NULL  registration_json=NULL  sidebar_custom_order=NULL  owner_session_id=NULL
```

`chat_session_sidebar_placements` / `chat_session_sidebar_group_memberships` 两张表 0 行也照常显示 → 侧栏不需要额外行。`workspaces` 表按 `workspace_id` 主键存 `root_paths_json`，所以 `workspace_id` 必须是真实存在的行——这就是脚本坚持"抄同 cwd 现成行"的原因。

## 升级后如何重新取证

```bash
# 1. 投影触发条件还在不在
strings -n 6 /Applications/Qoder.app/Contents/Resources/app.asar > /tmp/s.txt
python3 - <<'EOF'
import re
d=open('/tmp/s.txt',encoding='utf-8',errors='replace').read()
for k in ['cli-import','needsCliProjectionRefresh','replaceCliImportedMessages','sessionMigrationSources','transcriptRootDirectoryName']:
    print(k, d.count(k))
for m in list(re.finditer(r'hasMessages\(', d))[:5]:
    print(repr(d[max(0,m.start()-200):m.start()+400]))
EOF

# 2. 表结构与触发器（App 未运行时用 immutable=1，避免 SQLITE_CANTOPEN）
DB="$HOME/Library/Application Support/com.qoder.app.stable/main.sqlite"
sqlite3 "file:$DB?immutable=1" ".schema chat_sessions"
sqlite3 "file:$DB?immutable=1" "select name from sqlite_master where type='trigger' and tbl_name='chat_sessions';"

# 3. CLI 侧官方出口还在不在
strings -n 6 $(readlink -f /opt/homebrew/bin/qodercli) | grep -o -E '.{0,40}remote-control (start|status|qr-code).{0,20}' | sort -u
```

若 `cli-import` 计数变 0、或 `chat_sessions` 多了非空默认列，就重新按上面的取证路径核对，不要沿用本技能的 INSERT 列清单。
