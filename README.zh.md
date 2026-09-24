**中文** · [English](./README.md)

# daily-skills

个人 Agent Skill 仓库。每个顶层目录是一个自包含的 skill——一份 `SKILL.md` 加上它自己的脚本与资源。软链到 agent 的 skills 目录后，agent 会自动发现并在合适的时机调用。

没有构建步骤，没有第三方依赖：脚本只用 Python 3 标准库，凭证一律从环境变量读。

每个 skill 遵循 [Agent Skills](https://agentskills.io) 开放标准，该标准的 Client Showcase 已收录 40+ 个支持的客户端（Claude Code、Codex、Qoder、Kimi Code、CodeBuddy、OpenCode、Cursor 等）都能装。

## Skill 一览

| Skill | 做什么 | 需要的 key | 详细文档 |
| --- | --- | --- | --- |
| **infographic-gen** | 把文档 / SKILL / README 的要点生成信息图，默认沿用源材料语言。内置可爱卡通、极简商务、科技深色 HUD 三种三栏风格模板，另附 100 条样本 prompt 库（20+ 种视觉风格，可按序号直接出图）。指定画幅后同样能出封面图：微信公众号头图、小红书封面、音乐 / 播客封面等 | 二选一：`DASHSCOPE_API_KEY` 或 `SENSENOVA_API_KEY` | [infographic-gen/SKILL.md](infographic-gen/SKILL.md) |
| **cli-dispatch** | 向 Codex CLI（`codex exec`）、Qoder CLI（`qodercli -p`）、Claude Code（`claude -p`）、Kimi Code（`kimi -p`）或 Qwen Code（`qwen -p`）非交互派发任务：按任务级别选模型、推理力度和沙箱/权限，统一解析结果，支持会话续跑 | —（本地 CLI 登录态） | [cli-dispatch/SKILL.md](cli-dispatch/SKILL.md) |
| **qoder-import-cli-session** | 让终端里的 `qodercli` 会话出现在 Qoder 桌面 App 侧栏，可以直接打开查看完整历史消息 | 不需要，本机安装了 Qoder 即可 | [qoder-import-cli-session/SKILL.md](qoder-import-cli-session/SKILL.md) |

## infographic-gen

### 怎么使用

安装 skill 并配置好一种出图服务后，把源材料交给 Agent，再说明想要的结果。可以补充目标读者、发布平台、风格、画幅，以及必须准确出现的标题。

- 帮我把团队 wiki 的新人指南做成可爱卡通风信息图。
- 把这份文档整理成一张极简商务信息图，下周述职用，横版。
- 把这份网关设计文档做成科技深色风格的架构信息图。
- 按[样本库](infographic-gen/references/sample-library.md)第 13 条的风格出一张图。
- 同样的内容，用 sensenova 再出一版对比。
- 给这篇文章做一张 2.35:1 的公众号头图，标题是「……」。
- 做一张 3:4 的小红书封面，文字尽量少。
- 给这张 EP 设计一张 1:1 的专辑封面，深色极简风格。

也可以显式点名：Codex 里打 `$infographic-gen`，Claude Code / Qoder 里直接说“用 infographic-gen”。

infographic-gen 默认沿用源材料的语言。Agent 会提取重点、生成图片、检查文字和版式，再交付最终文件。图像模型仍可能处理不好密集文字或需要逐字准确的内容。如果每个字都不能出错，更适合改用可编辑的设计或排版工具。

### 内置模板

以下三张使用同一份源内容和 `qwen-image-3.0-pro` 生成，便于直接比较三种内置模板的视觉差异。

<table>
  <tr>
    <td align="center"><img src="infographic-gen/examples/skill-self-business-qwen.jpg" width="300" alt="极简商务风信息图"><br><sub><b>极简商务</b></sub></td>
    <td align="center"><img src="infographic-gen/examples/skill-self-cartoon-qwen.jpg" width="300" alt="可爱卡通风信息图"><br><sub><b>可爱卡通</b></sub></td>
    <td align="center"><img src="infographic-gen/examples/skill-self-tech-dark-qwen.jpg" width="300" alt="科技深色 HUD 信息图"><br><sub><b>科技深色 HUD</b></sub></td>
  </tr>
</table>

### 从 100 条样本库中精选的 15 种风格

样本库覆盖不同主题、语言、画幅、信息结构和视觉表现。以下 15 张用于快速预览；完整 100 条 prompt 可在[样本库索引](infographic-gen/references/sample-library.md)中按风格和场景查找。

<table>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-26-comic.jpg" width="240" alt="漫画风信息图"><br><sub><b>漫画</b> · #26</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-28-data-chart.jpg" width="240" alt="数据图表信息图"><br><sub><b>数据图表</b> · #28</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-34-watercolor.jpg" width="240" alt="水彩风信息图"><br><sub><b>水彩</b> · #34</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-35-ar.jpg" width="240" alt="AR 界面信息图"><br><sub><b>AR 界面</b> · #35</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-42-grid.jpg" width="240" alt="网格布局信息图"><br><sub><b>网格</b> · #42</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-45-mechanical.jpg" width="240" alt="机械风信息图"><br><sub><b>机械</b> · #45</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-51-chinese-ink.jpg" width="240" alt="国风水墨信息图"><br><sub><b>国风水墨</b> · #51</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-53-blueprint.jpg" width="240" alt="蓝图拼贴信息图"><br><sub><b>蓝图拼贴</b> · #53</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-54-archival.jpg" width="240" alt="档案复古信息图"><br><sub><b>档案复古</b> · #54</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-56-oil-baroque.jpg" width="240" alt="油画与巴洛克风信息图"><br><sub><b>油画 / 巴洛克</b> · #56</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-63-cyberpunk.jpg" width="240" alt="赛博朋克信息图"><br><sub><b>赛博朋克</b> · #63</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-64-biomed.jpg" width="240" alt="生物医学信息图"><br><sub><b>生物医学</b> · #64</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="infographic-gen/examples/sample-67-flat-vibrant.jpg" width="240" alt="扁平鲜亮风信息图"><br><sub><b>扁平鲜亮</b> · #67</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-70-iceberg.jpg" width="240" alt="冰山隐喻信息图"><br><sub><b>冰山隐喻</b> · #70</sub></td>
    <td align="center"><img src="infographic-gen/examples/sample-85-chalkboard.jpg" width="240" alt="黑板手绘信息图"><br><sub><b>黑板手绘</b> · #85</sub></td>
  </tr>
</table>

### 封面图

infographic-gen 也能生成封面图。告诉 Agent 图片要发到哪里、标题的准确文字和想要的风格，尺寸、裁剪和导出都由 Agent 处理。

| 用途 | 画幅 | 常用成品尺寸 |
| --- | --- | --- |
| 微信公众号头图 | 2.35:1 | 900 × 383 |
| 公众号贴图 / 小红书封面 | 3:4 竖版 | 1080 × 1440 |
| 音乐 / 播客 / 专辑封面 | 1:1 方图 | 1080 × 1080 |
| 常规信息图 | 16:9 横版 | 按使用场景确定 |

封面上的文字越少越稳。标题要逐字告诉 Agent，长说明留在文章或帖子里。图像模型可能改字、漏字或重复排版，因此 Agent 需要检查最终图片后再交付。

### 选择出图服务

infographic-gen 支持两种出图服务，配置其中一个即可：

| 服务 | Key | 适合场景 |
| --- | --- | --- |
| qwen，默认服务 | `DASHSCOPE_API_KEY` | 常规信息图，尤其是文字较多的版式 |
| sensenova | `SENSENOVA_API_KEY` | 偏好 SenseNova，或 qwen 暂时不可用时 |

只需要一个 key。请把它保存在本机环境中，不要贴进对话、文档或仓库。如果只配置了 SenseNova，需要在请求中说明使用 sensenova，因为默认服务是 qwen。出图可能产生费用或消耗免费额度，批量生成前先确认账户余额。

## cli-dispatch

把任务非交互地派发给 CLI coding agent：选定后端、按 `light` / `medium` / `heavy` 分级后，skill 会组装命令（模型、推理力度、沙箱/权限）、执行、解析结果，并回报可用于后续追问的 session id。

触发示例：

```
把 auth 模块的重构派发给 codex，heavy 级
把这个 bug 的修复派发给 qodercli，medium 级
用 kimi 分析这个目录的模块职责，只读就行
派发给 claude，跑完报告 session id
同样的任务再派给 qwen 跑一遍对比
将代码重构派发给 codex 进行评审，运行危险写、持久session、思考xhigh
```

也可以显式点名：直接说“用 cli-dispatch skill 将代码重构派发给 codex 进行评审”。

| 后端 | 派发命令 | 写任务需要的权限 | 续跑 | 验证版本 |
| --- | --- | --- | --- | --- |
| Codex CLI | `codex exec` | 沙箱逐级提权（`-s workspace-write` … `danger-full-access`） | `codex exec resume <id>` | v0.144.5 |
| Qoder CLI | `qodercli -p` | `--permission-mode bypass_permissions` | `-r <id>` | v1.1.1 |
| Claude Code | `claude -p` | `--permission-mode acceptEdits` / `bypassPermissions` | `-r <id>` / `-c` | v2.1.220 |
| Kimi Code | `kimi -p` | `--yolo` / `--auto` | `-S <id>`（不是 `-r`！） | v0.36.1 |
| Qwen Code | `qwen -p` | 权限模式在 `~/.qwen/settings.json` 中配置 | `-r <id>` / `-c` | v0.21.12 |

`scripts/parse_events.py` 把五种后端的事件流统一解析成同一个 JSON 对象（`session_id`、`answer`、`usage`、`errors`、`success`），派发侧代码不因后端而异——包括两个特例：qwen 的 `-o json` 输出的是 JSON 数组，kimi 的流里根本没有 `result` 行。所有后端的会话默认持久，后续追问直接复用完整上下文，不必重起。只要求目标 CLI 已安装并登录，不需要 API key。

## qoder-import-cli-session

用 `qodercli` 在终端发起的会话，通常不会出现在 Qoder 桌面 App 里。这个 skill 可以把已有的终端会话导入 App 侧栏，导入后可以直接打开并查看完整对话记录。

直接用自然语言告诉 Agent：

```
把这条 qodercli 会话导入 Qoder 桌面 App
把我最近一条 qodercli 会话导入 Qoder App
让刚才在终端使用的 Qoder 会话出现在 App 侧栏
```

Agent 会找到目标会话，检查当前是否适合导入，做好备份，再把它添加到 Qoder。看到提示后，重新打开 Qoder 并点击一次导入的会话，让 App 加载历史消息。之后 Agent 可以继续帮你确认是否导入成功。

导入前需要完全退出 Qoder 桌面 App，并停止正在运行的源 `qodercli` 会话。同一个项目目录还要在桌面 App 里至少有一条现成会话。如果没有，先用 Qoder 打开这个目录，随便新建一条会话，然后退出 App，再让 Agent 导入。

导入后的会话主要用于在桌面 App 中查看。要继续对话，请回到终端，用 `qodercli` 恢复原会话。如果不想继续在侧栏显示，也可以让 Agent 撤销导入。

目前已在 Qoder.app 0.3.4 和 qodercli 1.1.61 上验证。升级 Qoder 后，先让 Agent 重新检查兼容性。

## 安装

### 方式一：让 Agent 自己装

在 Claude Code、Codex 等支持 Agent Skills 的工具里直接说：

```
帮我安装这个 skill：https://github.com/jfojfo/daily-skills/tree/main/<skill-name>
```

Agent 会自己 clone 到对应目录，不用管路径。

### 方式二：clone + 软链

自己还要改 skill 就用这种，仓库里一改所有 agent 立刻生效，不用重新拷贝：

```bash
git clone https://github.com/jfojfo/daily-skills.git
cd daily-skills && REPO=$(pwd)
SKILL=infographic-gen   # 可选：infographic-gen、cli-dispatch、qoder-import-cli-session、…

# Claude Code
ln -s "$REPO/$SKILL" ~/.claude/skills/$SKILL

# Codex
ln -s "$REPO/$SKILL" ~/.codex/skills/$SKILL

# Qoder
ln -s "$REPO/$SKILL" ~/.qoder/skills/$SKILL
```

### 卸载

卸载删软链就行，不影响仓库：`rm ~/.claude/skills/<skill-name>`

### Agent 不支持 Skill 怎么办

把 `<skill-name>/SKILL.md` 全文下载下来，当项目规则文件用，或直接贴进对话让 agent 照着执行，效果一致——skill 本身就是一份结构化指令，不依赖任何运行时。

## License

[MIT](LICENSE)，覆盖本仓库自己的脚本与文档。

`infographic-gen/prompts/samples_infographic.jsonl` 中的 100 条样本 prompt 收集自公开来源，仅作为写 prompt 时的视觉参考，其自身权利归原作者所有。
