**中文** · [English](./README.md)

# jfo-skills

个人 Agent Skill 仓库。每个顶层目录是一个自包含的 skill——一份 `SKILL.md` 加上它自己的脚本与资源。软链到 agent 的 skills 目录后，agent 会自动发现并在合适的时机调用。

没有构建步骤，没有第三方依赖：脚本只用 Python 3 标准库，凭证一律从环境变量读。

每个 skill 遵循 [Agent Skills](https://agentskills.io) 开放标准，该标准的 Client Showcase 已收录 40+ 个支持的客户端（Claude Code、Codex、Qoder、Kimi Code、CodeBuddy、OpenCode、Cursor 等）都能装。

## Skill 一览

| Skill | 做什么 | 需要的 key | 详细文档 |
| --- | --- | --- | --- |
| **infographic-gen** | 把文档 / SKILL / README 的要点生成信息图，默认沿用源材料语言。内置可爱卡通、极简商务、科技深色 HUD 三种三栏风格模板，另附 100 条样本 prompt 库（20+ 种视觉风格，可按序号直接出图） | `DASHSCOPE_API_KEY` | [infographic-gen/SKILL.md](infographic-gen/SKILL.md) |

## 信息图示例

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

## 安装

### 方式一：让 Agent 自己装

在 Claude Code、Codex 等支持 Agent Skills 的工具里直接说：

```
帮我安装这个 skill：https://github.com/jfojfo/jfo-skills/tree/main/infographic-gen
```

Agent 会自己 clone 到对应目录，不用管路径。

### 方式二：clone + 软链

自己还要改 skill 就用这种，仓库里一改所有 agent 立刻生效，不用重新拷贝：

```bash
git clone https://github.com/jfojfo/jfo-skills.git
cd jfo-skills && REPO=$(pwd)

# Claude Code
ln -s "$REPO/infographic-gen" ~/.claude/skills/infographic-gen

# Codex
ln -s "$REPO/infographic-gen" ~/.codex/skills/infographic-gen

# Qoder
ln -s "$REPO/infographic-gen" ~/.qoder/skills/infographic-gen
```

### 卸载

卸载删软链就行，不影响仓库：`rm ~/.claude/skills/infographic-gen`

### Agent 不支持 Skill 怎么办

把 `infographic-gen/SKILL.md` 全文下载下来，当项目规则文件用，或直接贴进对话让 agent 照着执行，效果一致——skill 本身就是一份结构化指令，不依赖任何运行时。

## 环境变量

| 变量 | 用途 | 必需性 |
| --- | --- | --- |
| `DASHSCOPE_API_KEY` | 阿里云百炼（qwen-image-3.0-pro），infographic-gen 的默认 provider | 必需 |
| `SENSENOVA_KEY` | 商汤日日新（sensenova-u1-fast），备选 provider | 可选 |

写进 `~/.zshrc` 可持久化。三个脚本都在发请求前检查 key，缺失就退出并说明缺哪个变量，不会拿空 key 去打接口。**图像生成接口会产生费用或消耗免费额度**，批量跑样本库前先确认额度。

## 怎么触发

装好并配完 key，用自然语言说就行，agent 靠 `description` 自动匹配：

```
帮我把团队 wiki 的新人指南做成可爱卡通风
把这份文档的要点整理成一张商务风信息图，下周述职用，横版
这份网关设计文档，出一张科技深色 HUD 风格的信息图，给架构评审会用
把代码架构整理成架构信息图
生成一张科技深色风格的架构信息图
按样本库第 13 条的风格出一张图
同样的内容，用 sensenova 再出一版对比一下。
```

也可以显式点名：Codex 里打 `$infographic-gen`，Claude Code / Qoder 里直接说“用 infographic-gen”。

语言说明：infographic-gen 默认沿用源内容的语言。内置示例同时包含中文、英文和中英混排；图像模型仍可能在高密度文字中产生错字或变形，生成后需要验收成图。

## 仓库体积说明

`infographic-gen/examples/` 下的对比示例图是仓库的主要体积来源。只想看文档不需要示例图时可以浅克隆：`git clone --depth 1`。

## License

[MIT](LICENSE)，覆盖本仓库自己的脚本与文档。

`infographic-gen/prompts/samples_infographic.jsonl` 中的 100 条样本 prompt 收集自公开来源，仅作为写 prompt 时的视觉参考，其自身权利归原作者所有。
