# Provider 与脚本

## 选择 provider

| Provider | 模型 | 环境变量 | 默认尺寸 | 适用情况 |
|---|---|---|---|---|
| `qwen`（默认） | `qwen-image-3.0-pro` | `DASHSCOPE_API_KEY` | `2560*1440` | 文字密度较高的常规信息图 |
| `sensenova` | `sensenova-u1-fast` | `SENSENOVA_KEY` | `2752x1536` | 需要 OpenAI images API 兼容接入或 qwen 不可用 |

只配置实际使用的 provider。API key 只从环境变量读取，不要写入仓库、prompt、日志或最终答复。生成调用可能产生费用；批量生成前确认范围。

```bash
export DASHSCOPE_API_KEY=sk-xxxx
export SENSENOVA_KEY=sk-xxxx
```

如果模型可用性、定价或额度影响决策，先查看 provider 的最新官方信息。

## 运行脚本

从 skill 根目录执行：

```bash
# qwen：SIZE 使用 WIDTH*HEIGHT
python3 scripts/gen_qwen_image.py PROMPT_FILE OUT_PATH [SIZE]

# sensenova：SIZE 使用 WIDTHxHEIGHT
python3 scripts/gen_sensenova_u1.py PROMPT_FILE OUT_PATH [SIZE]

# 按 0-based 样本编号生成；默认 qwen，并使用样本自带尺寸
python3 scripts/gen_from_sample.py INDEX OUT_PATH [--provider qwen|sensenova]
```

脚本会在请求前检查 key、创建输出目录并下载图片。先确认 prompt 文件存在且已经替换演示内容，再发出请求。

### 常用尺寸

| 用途 | qwen 写法 | sensenova 写法 | 说明 |
|---|---|---|---|
| 横版三栏，默认 | `2560*1440` | `2752x1536` | 文字空间最充足 |
| 横版低成本尝试 | `1664*928` | 按 provider 支持尺寸选择 | 适合先验证构图 |
| 方形 | `1024*1024` | `1024x1024` | 三栏容易拥挤，优先网格 |
| 竖版长图 | `928*1664` | 按 provider 支持尺寸选择 | 适合单列流程 |

不要把 qwen 的 `*` 和 sensenova 的 `x` 混用。样本脚本会自动转换分隔符。

## qwen 接入

`gen_qwen_image.py` 使用 DashScope 同步接口：

```text
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

响应图片路径为 `output.choices[0].message.content[0].image`。不要改用以下端点：

- `/api/v1/services/aigc/text2image/image-synthesis`：可能返回 `InvalidParameter: url error`
- `/compatible-mode/v1/images/generations`：该模型不走此路径

错误处理：

- `[err] DASHSCOPE_API_KEY env var required`：配置环境变量后重试。
- `url error`：检查是否误用了 text-to-image 端点。
- 响应中没有 image URL：保留截断后的响应结构排查，不要打印授权头。

## sensenova 接入

`gen_sensenova_u1.py` 默认使用 OpenAI 兼容端点：

```text
POST https://token.sensenova.cn/v1/images/generations
```

响应支持 `data[0].url` 或 `data[0].b64_json`。返回 URL 为临时链接，有效期 1 小时，脚本生成后立即下载保存。需要自建兼容网关时设置：

```bash
export SENSENOVA_GATEWAY=https://your-gateway.example/v1
```

水印控制：payload 中显式传 `watermark`（boolean，官方默认 `true` 为加 Logo 水印）。脚本默认 `false` 去水印，可用环境变量覆盖：

```bash
export SENSENOVA_WATERMARK=true   # 恢复官方 Logo 水印
```

去水印当前免费公测，后续将转为付费功能，注意官方计费公告。

脚本会自动补 `/v1`。错误处理：

- `[err] SENSENOVA_KEY env var required`：配置环境变量后重试。
- `auth_unavailable: no auth available`：自建网关缺少 SenseNova 上游凭证，联系网关维护方。
- HTTP 404：检查 base URL 是否指向正确的 `/v1` 路径。
- 空 `data`：检查模型名、网关响应和账号权限。

## 验证而不产生费用

不调用远端 API 时，可以执行以下检查：

```bash
python3 scripts/gen_from_sample.py --help
python3 scripts/gen_qwen_image.py
python3 scripts/gen_sensenova_u1.py
```

后两个命令因缺少参数返回用法并以非零状态退出，这是预期行为。不要为了 smoke test 使用真实 key 发起生成请求。
