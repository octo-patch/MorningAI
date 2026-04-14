# Message Digest Template

This template defines the exact output format for `message_{DATE}.md`.

---

## Language-Specific Text

### Headers

| `--lang` | Header Line 1 | Header Line 2 |
|----------|---------------|----------------|
| `zh` | `AI 每日速报 {YYYY-MM-DD}` | `共 {N} 条重要更新` |
| `en` | `AI Daily Digest {YYYY-MM-DD}` | `{N} notable updates today` |
| `ja` | `AI デイリーダイジェスト {YYYY-MM-DD}` | `本日の注目 {N} 件` |

### Footer

| `--lang` | Footer |
|----------|--------|
| `zh` | `Powered by MorningAI \| 完整报告: report_{DATE}.md` |
| `en` | `Powered by MorningAI \| Full report: report_{DATE}.md` |
| `ja` | `Powered by MorningAI \| 完全レポート: report_{DATE}.md` |

---

## Template Structure

```
{Header Line 1}

{Header Line 2}

{Item 1}

{Item 2}

...

{Item N}

---
{Reference Links}

---
{Footer}
```

---

## Item Template

### Standard Item

```
{emoji} **{Entity} {Event Description}**
{1-2 sentence summary with key metrics and specifics.}
```

**Emoji selection:**
- Score 9-10 → `🔥`
- Score 7-8 → `⭐`
- Score 5-6 → `🔷`

**Title rules:**
- Bold the entire title
- Include entity name + concise event description
- Keep titles under 30 characters (Chinese) or 60 characters (English) when possible
- Do NOT include score numbers

**Summary rules:**
- Condense to 1-2 sentences maximum
- Include the most important specific details: numbers, versions, benchmarks, pricing
- No filler phrases like "major update" without specifics
- End with a period

### GitHub Trending Item (Special)

When an item is from GitHub Trending or has notable star/fork metrics:

```
🔥 **GitHub 热门项目：{repo-name}（Stars 暴涨！）**
⭐ {star_count}(+{delta}) | {one-line description}
```

(Use Chinese format shown above for `--lang zh`, adapt for other languages)

---

## Reference Links Section

### Bottom Format (`MESSAGE_LINKS=bottom`, default)

```
---
[1] {Entity Event Short Label} - {source_url}
[2] {Entity Event Short Label} - {source_url}
...
```

- One link per item, in the same order as items appear
- Short label: `{Entity} {Event}` (e.g., "Anthropic Claude 4.5 Sonnet")
- Full URL from `source_url` field

### Inline Format (`MESSAGE_LINKS=inline`)

Each item appends a link line:

```
{emoji} **{Entity} {Event Description}**
{Summary sentence.}
🔗 {source_url}
```

When using inline format, omit the reference links section at the bottom.

---

## Complete Example (Chinese)

```
AI 每日速报 2026-04-08

共 8 条重要更新

🔥 **Anthropic 发布 Claude 4.5 Sonnet**
新一代中端模型，编程能力提升18%（SWE-Bench），200K上下文窗口，输出速度快40%。API 和 claude.ai 即刻可用。

⭐ **Google Gemini 2.5 Flash 进入公测**
Flash级模型支持原生多模态推理，100万上下文窗口。AI Studio 免费可用。

⭐ **Cursor 后台 Agent 正式上线**
自主后台Agent正式发布，支持多文件重构、测试生成和自动提PR，Pro 最多10个并发。

⭐ **DeepSeek 开源 V3-0407 模型**
更新版V3模型，671B参数MoE架构，MIT协议完全商用。权重已在HuggingFace发布。

⭐ **OpenAI 开源 Codex CLI**
终端编程Agent开源发布，支持建议、自动编辑和全自动三种模式，MIT协议。

⭐ **LMSYS Chatbot Arena 四月排名更新**
Claude 4.5 Sonnet 升至总榜第2（ELO 1287），Gemini 2.5 Pro 保持编程类第1。

⭐ **GitHub Copilot Coding Agent 公测**
GitHub自主Agent可处理Issue并提交PR，在安全云沙箱中运行，Pro+和Enterprise免费。

⭐ **Windsurf 获得2亿美元C轮融资**
AI IDE公司获编程工具领域最大单轮融资，估值30亿美元，计划招聘200名工程师。

---
[1] Anthropic Claude 4.5 Sonnet - https://x.com/AnthropicAI/status/example
[2] Google Gemini 2.5 Flash - https://x.com/GoogleDeepMind/status/example
[3] Cursor Background Agents - https://x.com/cursor_ai/status/example
[4] DeepSeek V3-0407 - https://github.com/deepseek-ai/DeepSeek-V3
[5] OpenAI Codex CLI - https://github.com/openai/codex
[6] LMSYS Chatbot Arena - https://lmarena.ai
[7] GitHub Copilot Coding Agent - https://github.blog/changelog/copilot-coding-agent
[8] Windsurf Series C - https://techcrunch.com/2026/04/07/windsurf-raises-200m

---
Powered by MorningAI | 完整报告: report_2026-04-08.md
```
