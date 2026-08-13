# 样本库索引

**100 条**公开样本 prompt，来自 [samples_infographic.jsonl](../prompts/samples_infographic.jsonl)。覆盖从赛博朋克到水彩、从蓝图到油画、从科普图表到漫画海报的多种视觉风格，可作为编写自己 prompt 时的视觉参考或起手式。

- 语言：53 英 / 47 中
- 尺寸：横版 47 张（2720×1504、2496×1664、2368×1760、2272×1824、3136×1312 banner），方形 19 张（2048×2048），竖版 34 张（1504×2720 最多，13 张）

## 目录

- [怎么用](#怎么用)
- [风格速查](#风格速查按风格归类)
- [按场景反查](#按场景反查)
- [完整列表](#完整列表)
- [维护](#维护)

## 怎么用

1. 浏览[风格速查表](#风格速查按风格归类)挑一条接近目标氛围的
2. 用脚本快速出图体验该风格效果：
   ```bash
   export DASHSCOPE_API_KEY=sk-...
   python scripts/gen_from_sample.py <序号> /tmp/sample_NN.png
   # 例如:  python scripts/gen_from_sample.py 13 /tmp/cyberpunk.png
   ```
3. 复制对应样本的 prompt 作为起手式：
   ```bash
   jq -r ".prompt" prompts/samples_infographic.jsonl | sed -n '<N+1>p' > /tmp/my.txt
   # 然后编辑 /tmp/my.txt 替换主题/标题/各栏内容
   python scripts/gen_qwen_image.py /tmp/my.txt /tmp/out.png 2560*1440
   ```

## 风格速查（按风格归类）

| 风格标签 | 数量 | 序号（节选） | 一句话定位 |
|---|---:|---|---|
| **circular** 环形/螺旋 | 32 | 0, 4, 15, 17, 19, 21, 29, 32, 33, 43, 47, 49, 57, 61, 64, 68, 77, 78, 80, 84, 88, 92, 96 | 中心 → 外圈/步骤闭环；最通用的"流程"骨架 |
| **sci-modern** 科技未来 | 22 | 1, 13, 22, 23, 27, 35, 38, 41, 46, 57, 63, 64, 67, 79, 82, 88, 93, 96, 98, 99 | HUD/全息/玻璃质感；架构图与数据看板首选 |
| **hand-drawn** 手绘 | 18 | 3, 20, 24, 31, 33, 34, 36, 44, 50, 53, 65, 68, 71, 78, 85, 86 | 米白纸张质感、亲切随性；科普/教程/生活 |
| **data-chart** 数据图表 | 18 | 5, 6, 7, 8, 9, 17, 28, 29, 38, 46, 61, 70, 74, 86, 88, 92, 94, 96 | 含真实柱/饼/折线 + KPI 数字 |
| **mechanical** 机械装置 | 13 | 13, 19, 27, 40, 45, 46, 58, 60, 61, 67, 79, 86, 89 | 齿轮/管线/解构感；理工/制造业 |
| **cyberpunk** 赛博朋克 | 12 | 0, 1, 10, 15, 22, 27, 37, 57, 63, 88, 93, 96 | 霓虹/8-bit/复古 UI；最出片的深色调 |
| **watercolor** 水彩 | 9 | 3, 18, 19, 25, 31, 34, 47, 77, 86 | 柔和渐变；食物/自然/教程 |
| **biomed** 生物医学 | 9 | 5, 16, 23, 39, 41, 64, 88, 94, 99 | DNA/细胞/分子/解剖 |
| **grid** 网格/四象限 | 9 | 17, 36, 42, 51, 63, 69, 79, 86, 92 | 严格几何分区；对比/对照 |
| **blueprint** 工程蓝图 | 9 | 43, 53, 58, 69, 71, 75, 76, 77, 89 | 深蓝底 + 白线 + 标注；机械/航天 |
| **comic** 漫画/波普 | 6 | 26, 49, 50, 69, 73, 94 | 粗描边/对话框/分格叙事 |
| **archival** 档案复古 | 5 | 2, 47, 54, 55, 70 | 棕褐/做旧；历史/法律/政策 |
| **chalkboard** 黑板教学 | 3 | 36, 68, 85 | 暗底白粉笔字；课堂笔记 |
| **tree** 树状/族谱 | 3 | 54, 71, 77 | 主干分叉；规划/族系 |
| **flat-vibrant** 扁平鲜亮 | 3 | 67, 90, 97 | 高饱和扁平块面；现代品牌风 |
| **luxury** 奢华金箔 | 2 | 21, 93 | 香槟金 + 装饰边框 |
| **poster** 海报样式 | 2 | 60, 95 | 单视点 + 大标语；宣传 |
| **chinese-trad** 中国风/水墨 | 2 | 16, 51 | 国风元素 |
| **paper-cut** 剪纸/折纸 | 1 | 43 | 层次叠加质感 |
| **oil-baroque** 油画/巴洛克 | 1 | 56 | 金框文艺复兴 |
| **iceberg** 冰山隐喻 | 1 | 70 | 水上可见 vs 水下隐藏 |

## 按场景反查

- **办公/正经汇报**（白皮书/季报/述职）→ 17, 28, 29, 38, 46, 67, 92 / 自有 [`business.txt`](../prompts/business.txt)
- **技术架构/数据看板** → 13, 22, 27, 35, 38, 41, 46, 63, 79, 88, 96, 99 / 自有 [`tech-dark.txt`](../prompts/tech-dark.txt)
- **科普教程/课堂笔记** → 3, 19, 31, 34, 36, 44, 65, 68, 85（手绘/水彩/黑板）
- **儿童/团队内训/萌系** → 自有 [`cartoon.txt`](../prompts/cartoon.txt)
- **媒体宣发/视觉海报** → 0, 21, 26, 49, 50, 56, 60, 95
- **金融/医疗/法律 严肃文档** → 5, 28, 29, 39, 47, 54, 55, 61, 70, 81
- **流程闭环/五步法/环形** → 0, 4, 15, 17, 19, 23, 29, 32, 33, 42, 47, 49, 57, 61, 64, 68, 77, 78, 80, 84, 88, 92, 93, 96
- **隐喻可视化**（具象比喻贯穿） → 5（染色体）, 19（火星探测）, 22（餐饮）, 23（液氮/植物茎尖）, 43（剪纸演化）, 47（UFO/档案）, 54（树状/根系）, 70（冰山）, 86（习惯养成）
- **中文标题为主**（共 47 条）→ 0, 1, 3, 13, 18, 20, 22-24, 27, 30, 33-34, 37-41, 44-46, 48, 50, 53, 58-60, 62, 64-67, 72-74, 81-83, 85-87, 89, 90, 95-99

## 完整列表

> 朝向：L = 横版 / P = 竖版 / S = 方形

| # | 尺寸 | 朝向 | 语言 | 风格标签 | 主题（缩写） |
|--:|---|---|---|---|---|
|  0 | 3136×1312 | L | zh | cyberpunk, sci-modern, circular           | 翼起进化：5G-A 极速时代 |
|  1 | 3136×1312 | L | zh | cyberpunk, sci-modern                     | 酒店智能化与市场趋势洞察 |
|  2 | 3136×1312 | L | en | archival, circular                        | Core Health Benefits of Sanqi |
|  3 | 3136×1312 | L | zh | watercolor, hand-drawn                    | 水为何在冬结冰而在夏流淌 |
|  4 | 2720×1504 | L | en | circular                                  | SCOUTING（环形主题） |
|  5 | 2720×1504 | L | en | biomed, data-chart                        | Polyploidy in chromosomes |
|  6 | 2720×1504 | L | en | data-chart                                | Urban Construction |
|  7 | 2720×1504 | L | en | data-chart                                | La Niña 全球足迹 |
|  8 | 2720×1504 | L | en | data-chart                                | Healthcare Risk Management（医疗诉讼胜诉率） |
|  9 | 2720×1504 | L | en | data-chart                                | Peak Power Density（机架功率密度演进） |
| 10 | 2720×1504 | L | en | cyberpunk                                 | Base Saturation of Fast Fashion |
| 11 | 2720×1504 | L | en | —                                         | SMART SAVER KIT |
| 12 | 2720×1504 | L | en | —                                         | Love Unlocked: Read Between the Lines |
| 13 | 2720×1504 | L | zh | sci-modern, mechanical                    | 复古像素 + 控制台界面 |
| 14 | 2720×1504 | L | en | —                                         | 2024 Driving License Updates |
| 15 | 2720×1504 | L | en | cyberpunk, circular                       | Mid-Autumn Festival 月饼指南 |
| 16 | 2720×1504 | L | en | biomed, chinese-trad                      | Modern Hanfu Pathways |
| 17 | 2720×1504 | L | en | circular, grid, data-chart                | What is Cyclical Unemployment |
| 18 | 2720×1504 | L | zh | watercolor                                | 免费定位手环·守护易走失人群 |
| 19 | 2720×1504 | L | en | watercolor, hand-drawn, circular, mech    | Hidden Rover Secrets（火星车科普） |
| 20 | 2720×1504 | L | zh | hand-drawn                                | 停电通知 |
| 21 | 2720×1504 | L | en | circular, luxury                          | VISION VOGUE · 时尚眼镜 |
| 22 | 2720×1504 | L | zh | cyberpunk, sci-modern                     | 猪肝烹饪方法与食谱 |
| 23 | 2720×1504 | L | zh | biomed, sci-modern, circular              | 植物茎尖冷冻保存方案 |
| 24 | 2496×1664 | L | zh | hand-drawn                                | 社区治理·让爱串门 |
| 25 | 2496×1664 | L | en | watercolor                                | Urbanization Impacts |
| 26 | 2496×1664 | L | en | comic                                     | Pumpkin Preparations |
| 27 | 2496×1664 | L | zh | cyberpunk, sci-modern, mechanical         | 心理学与社会学知识普及 |
| 28 | 2496×1664 | L | en | data-chart                                | R-Squared Explained |
| 29 | 2496×1664 | L | en | circular, data-chart                      | American Options 金融策略 |
| 30 | 2368×1760 | L | zh | —                                         | 徒手攀岩小知识 |
| 31 | 2368×1760 | L | en | watercolor, hand-drawn                    | 宜宾 7-day Weather Forecast |
| 32 | 2368×1760 | L | en | circular                                  | Choosing Your Pet Chameleon |
| 33 | 2368×1760 | L | zh | hand-drawn, circular                      | 趣味跳房子：扩展玩法 |
| 34 | 2368×1760 | L | zh | watercolor, hand-drawn                    | 蒜香排骨烹饪流程 |
| 35 | 2368×1760 | L | en | sci-modern, circular                      | AR 增强现实界面 |
| 36 | 2368×1760 | L | en | chalkboard, hand-drawn, grid              | Crop Physiology |
| 37 | 2368×1760 | L | zh | cyberpunk, sci-modern                     | 小米电暖器机型对比 |
| 38 | 2368×1760 | L | zh | sci-modern, data-chart                    | Auto Specs: Velocity |
| 39 | 2368×1760 | L | zh | biomed                                    | 浅表切口手术部位感染 |
| 40 | 2368×1760 | L | zh | mechanical                                | 变异性·标准差·管理会计 |
| 41 | 2368×1760 | L | zh | biomed, sci-modern                        | 深渊生存：高压极寒适应 |
| 42 | 2272×1824 | L | en | circular, grid                            | Sustainability Log |
| 43 | 2272×1824 | L | en | blueprint, circular, paper-cut            | Evolution of Yi Yang Qianxi（剪纸） |
| 44 | 2272×1824 | L | zh | hand-drawn                                | 绘本治愈风·微观世界 |
| 45 | 2272×1824 | L | zh | mechanical                                | 铬酸银沉淀反应化学原理 |
| 46 | 2272×1824 | L | zh | sci-modern, circular, mech, data-chart    | 第一季度财务报告分析 |
| 47 | 2048×2048 | S | en | archival, watercolor, hand-drawn, circ    | Strange Lights（UFO 档案） |
| 48 | 2048×2048 | S | zh | circular                                  | 职称评审成分表 |
| 49 | 2048×2048 | S | en | comic, circular                           | VISA DENIED?! |
| 50 | 2048×2048 | S | zh | comic, hand-drawn                         | EARTHQUAKE: 活下去 |
| 51 | 2048×2048 | S | en | grid, chinese-trad                        | Shattered Silks 中国风 |
| 52 | 2048×2048 | S | en | —                                         | Spring Festival Service Guide |
| 53 | 2048×2048 | S | zh | blueprint, hand-drawn                     | China Aerospace |
| 54 | 2048×2048 | S | en | archival, tree                            | Earthen Souls: Rural Verticality |
| 55 | 2048×2048 | S | en | archival                                  | Guizhou Civil Judgment |
| 56 | 2048×2048 | S | en | oil-baroque                               | The Renaissance of Paper |
| 57 | 2048×2048 | S | en | cyberpunk, sci-modern, circular           | Core Psychology of Emotions |
| 58 | 2048×2048 | S | zh | blueprint, mechanical                     | 体育人物法律问题剖面图 |
| 59 | 2048×2048 | S | zh | —                                         | 个人成长与命运·浮世绘 |
| 60 | 2048×2048 | S | zh | mechanical, poster                        | 时尚潮流产品推广 |
| 61 | 2048×2048 | S | en | circular, mechanical, data-chart          | Investment Fees & Net Returns |
| 62 | 2048×2048 | S | zh | —                                         | 疫情期间活动防控指南 |
| 63 | 2048×2048 | S | en | cyberpunk, sci-modern, grid               | Eye Shadow: Virtual Introduction |
| 64 | 2048×2048 | S | zh | biomed, sci-modern, circular              | 基因传递·孟德尔定律 |
| 65 | 2048×2048 | S | zh | hand-drawn                                | Earth's Rotation |
| 66 | 1824×2272 | P | en | —                                         | The Golden Bloom: Osmanthus Care |
| 67 | 1824×2272 | P | zh | sci-modern, mechanical, flat-vibrant      | 中科院科研与育人（2×2 网格） |
| 68 | 1824×2272 | P | en | chalkboard, hand-drawn, circular          | Pikachu & Pokémon Culture |
| 69 | 1824×2272 | P | en | comic, blueprint, grid                    | International Student Pathways |
| 70 | 1824×2272 | P | en | archival, iceberg, data-chart             | Social Insurance Policies（冰山） |
| 71 | 1824×2272 | P | en | blueprint, hand-drawn, tree               | Degree Upgrade Planning |
| 72 | 1824×2272 | P | zh | —                                         | 网络小说类型与特点（金字塔） |
| 73 | 1824×2272 | P | zh | comic                                     | 儿童营养补充全指南（漫画） |
| 74 | 1824×2272 | P | zh | data-chart                                | 潮玩·随机消费新玩法 |
| 75 | 1216×1600 | P | en | blueprint                                 | 学术论文版式（typesetting） |
| 76 | 1216×1600 | P | en | blueprint                                 | 学术论文首页（typesetting） |
| 77 | 1664×2496 | P | en | blueprint, watercolor, tree, circular     | Sci-Tech Independent Innovation |
| 78 | 1760×2368 | P | en | hand-drawn, circular                      | Program Impact At A Glance |
| 79 | 1760×2368 | P | en | sci-modern, circular, grid, mechanical    | 国潮 Exhibition Adjustments |
| 80 | 1760×2368 | P | en | circular                                  | Age Discrimination Flourishing |
| 81 | 1664×2496 | P | zh | —                                         | 房屋买卖合同·交易与法律风控 |
| 82 | 1664×2496 | P | zh | sci-modern, circular                      | 绿茵定格·巨星轶事（战术分析） |
| 83 | 1664×2496 | P | zh | —                                         | 旬之味·主厨定制三部曲 |
| 84 | 1664×2496 | P | en | circular                                  | Young Pioneers of China Admission |
| 85 | 1664×2496 | P | zh | chalkboard, hand-drawn                    | 超实用居家生活小贴士 |
| 86 | 1664×2496 | P | zh | watercolor, hand-drawn, grid, mech, data  | 好习惯养成指南（四象限） |
| 87 | 1504×2720 | P | zh | —                                         | 乡村振兴动态图谱 |
| 88 | 1504×2720 | P | en | cyberpunk, biomed, sci-modern, circ, data | IP is the Ultimate Asset |
| 89 | 1504×2720 | P | zh | blueprint, mechanical                     | 企业社会价值跃迁之路 |
| 90 | 1504×2720 | P | zh | flat-vibrant                              | Rhymes of Nature·诗与思 |
| 91 | 1504×2720 | P | en | —                                         | College Entrance Pathway Reform |
| 92 | 1504×2720 | P | en | circular, grid, data-chart                | Web Accessibility Compilation |
| 93 | 1504×2720 | P | en | cyberpunk, sci-modern, circular, luxury   | Embroidery 101 |
| 94 | 1504×2720 | P | en | comic, biomed, data-chart                 | A Complete Guide to Project F... |
| 95 | 1504×2720 | P | zh | poster                                    | 救援服务全解析（实用指南） |
| 96 | 1504×2720 | P | zh | cyberpunk, sci-modern, circ, data         | 磷化工行业核心维度对比 |
| 97 | 1504×2720 | P | zh | flat-vibrant                              | 职场成长×企业文化共生 |
| 98 | 1504×2720 | P | zh | sci-modern                                | 地球四季与生命律动 |
| 99 | 1504×2720 | P | zh | biomed, sci-modern                        | 根系微观·矿物质吸收 |

## 维护

- 新增样本：往 [samples_infographic.jsonl](../prompts/samples_infographic.jsonl) 追加一行 JSON `{"prompt": "...", "width": W, "height": H}`，再补充一行到上表
- 字段：`prompt`（必填）, `width` / `height`（必填）, `seed`（可选）
- 更新分类统计和场景索引后，核对样本编号仍为 0-based 且与 JSONL 行序一致
