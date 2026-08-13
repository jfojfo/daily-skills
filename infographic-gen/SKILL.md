---
name: infographic-gen
description: 将 SKILL、README、技术规范、产品说明、周报等文本提炼为结构清晰的信息图，并通过内置模板或样本库生成图片。支持可爱卡通、极简商务、科技深色 HUD 三种模板，以及 qwen-image-3.0-pro 和 sensenova-u1-fast 两个 provider。用于“把文档做成信息图/海报/导读图/cheat sheet”“生成三栏总结图”“用某种视觉风格呈现要点”等请求。
---

# 信息图生成

将源材料压缩为一张准确、易读的信息图。默认沿用源材料的主要语言，不自动翻译或添加另一种语言；其他默认值为极简商务风、16:9 三栏布局和 qwen provider。

## 执行流程

1. 读取源材料，确认受众、用途、画幅和输出路径。沿用用户提供文案的语言；用户明确指定语言时，按要求组织文案。缺少其他偏好时采用默认值，不要为非关键选项停下来询问。
2. 提取 5–8 个核心概念，只使用源材料中能够确认的事实。保留关键数字、专有名词和限制条件，不要补造指标或结论。
3. 组织信息层级：
   - 顶部：主标题 + 一句副标题
   - 左栏：核心能力、背景或“是什么”
   - 中栏：流程、阶段或“怎么做”
   - 右栏：规则、风险、建议或“注意什么”
   - 底部：一句核心目标或结论
4. 按下表选择风格。需要三种内置风格之外的视觉语言时，读取 [样本库索引](references/sample-library.md)，只挑 1–2 条最接近的样本作为骨架。
5. 复制对应模板到临时 prompt 文件，替换模板中的演示主题、标题、栏目和条目。不要直接用未修改的模板生成用户内容。
6. 读取 [Provider 与脚本](references/providers.md)，检查所选 provider 的环境变量，再运行脚本。不要输出、记录或写入 API key。
7. 打开生成图验收文字、事实、结构和风格。根据具体问题缩短文案、强化位置约束或补充禁忌词后再生成；每次重试都可能产生费用。
8. 返回最终图片，并简要说明所用风格、provider 和尺寸。

## 风格选择

| 风格 | 适用场景 | 模板 |
|---|---|---|
| `business`（默认） | 正式汇报、产品说明、白皮书、周报、述职 | [business.txt](prompts/business.txt) |
| `cartoon` | 新人引导、教育科普、轻松社媒、庆祝内容 | [cartoon.txt](prompts/cartoon.txt) |
| `tech-dark` | 架构评审、安全报告、技术演示、数据看板 | [tech-dark.txt](prompts/tech-dark.txt) |
| 样本库风格 | 水彩、蓝图、漫画、环形、竖版等非标准需求 | [sample-library.md](references/sample-library.md) |

正式、问责性或包含风险/资源诉求的材料优先使用 `business`。技术主题只有在需要明显科技视觉时才使用 `tech-dark`。

## Prompt 约束

- 每栏保留 3–6 条；条目使用“短标题：一句说明”，避免整段搬运原文。
- 明确写出画幅、栏目位置、字体气质、配色、图标类型和禁止元素。
- 只使用用户或源材料明确提供的文案，不自动翻译、补充或混入其他语言。
- 为每个条目指定具体图标；不要只写“配一个好看的图标”。
- 控制单页信息密度。文字拥挤时先删减条目，不要先缩小字号。
- 对必须逐字准确的文案保持克制。生成式图像模型可能产生错字；精确排版是硬性要求时，应改用可编辑的设计或排版工作流。

需要改版式、写自定义 prompt 或排查风格漂移时，读取 [Prompt 设计指南](references/prompt-design.md)。

## 生成命令

从本 skill 目录执行：

```bash
# 默认：qwen + 商务风 + 16:9
cp prompts/business.txt /tmp/infographic-prompt.txt
# 编辑临时文件，替换其中全部演示内容
python3 scripts/gen_qwen_image.py /tmp/infographic-prompt.txt /tmp/infographic.png

# 可选：同一 prompt 改用 sensenova
python3 scripts/gen_sensenova_u1.py /tmp/infographic-prompt.txt /tmp/infographic-sensenova.png

# 直接生成 0-based 编号的样本，并沿用样本尺寸
python3 scripts/gen_from_sample.py 13 /tmp/sample-13.png
```

只有在用户明确要复现某条样本时才直接运行 `gen_from_sample.py`。通常应提取样本 prompt 的构图骨架，再替换成用户内容。

## 资源导航

| 需求 | 读取或使用 |
|---|---|
| 选择样本、尺寸或特殊风格 | [references/sample-library.md](references/sample-library.md) |
| 组织内容、定版式、修复风格问题 | [references/prompt-design.md](references/prompt-design.md) |
| 配置模型、运行脚本、排查 API 错误 | [references/providers.md](references/providers.md) |
| 比较历史出图效果 | `examples/`；仅在确实需要视觉对比时打开相关图片 |
| 生成内置风格 | `prompts/*.txt` + `scripts/gen_qwen_image.py` 或 `scripts/gen_sensenova_u1.py` |
| 按样本编号生成 | `prompts/samples_infographic.jsonl` + `scripts/gen_from_sample.py` |

## 验收清单

- [ ] 标题、栏目名、数字和专有名词与源材料一致
- [ ] 信息层级一眼可辨，阅读顺序明确，条目没有明显截断或重复
- [ ] 文字基本清晰；没有大段乱码、叠字或非预期语言混入
- [ ] 风格、配色、图标和禁忌元素符合选择
- [ ] 输出文件存在、能够打开，尺寸与用途匹配

验收失败时只针对失败项调整 prompt。不要在没有诊断原因的情况下连续重复调用。
