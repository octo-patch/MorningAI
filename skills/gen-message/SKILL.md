---
name: gen-message
description: Generate concise message digest with image for sharing on messaging platforms (WeChat, Telegram, Slack, etc.)
---

## Objective

Transform the daily AI news report data into a concise, copy-paste-friendly **message digest** optimized for sharing on messaging platforms. Produces two output files:

1. **Text digest** (`message_{DATE}.md`) — bold titles, one-line summaries, reference links
2. **Digest image** (`message_{DATE}.png`) — 9:16 portrait infographic with compact card layout

The text is designed for direct copy-paste into any messaging app. The image provides a visual companion for platforms that support image attachments.

---

## Output Specs

### Text File: `message_{DATE}.md`

| Property | Value |
|----------|-------|
| Format | Markdown (renders as plain text in most messaging apps) |
| Encoding | UTF-8 |
| Sections | Header → Items → Reference Links → Footer |

### Image File: `message_{DATE}.png`

| Property | Value |
|----------|-------|
| Format | PNG |
| Aspect Ratio | 9:16 portrait (optimized for mobile chat) |
| Layout | Single-column vertical card stack |
| Content | Same items as text digest, compact visual format |

---

## Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MESSAGE_ENABLED` | bool | `false` | Master switch for message digest generation |
| `MESSAGE_MIN_SCORE` | float | `5` | Minimum importance score to include an item |
| `MESSAGE_MAX_ITEMS` | int | `10` | Maximum number of items in the digest |
| `MESSAGE_LANG` | string | (from `--lang`) | Language override for the digest |
| `MESSAGE_IMAGE_STYLE` | string | (from `IMAGE_STYLE`) | Visual style override for the digest image |
| `MESSAGE_LINKS` | string | `bottom` | Link placement: `bottom` (reference list) or `inline` (after each item) |

---

## Content Selection Rules

1. **Read data**: Load `data_{DATE}.json` from the working directory
2. **Filter by score**: Only items with `importance >= MESSAGE_MIN_SCORE`
3. **Sort**: By importance score descending (highest first)
4. **Limit**: Take top N items (from `MESSAGE_MAX_ITEMS`)
5. **Translate**: If data language differs from `MESSAGE_LANG`, translate summaries. Entity names (proper nouns) stay unchanged.

---

## Text Generation Rules

### Language-Specific Headers

| Language | Header Text | Item Count Format |
|----------|-------------|-------------------|
| `zh` | `AI 每日速报 {DATE}` | `共 {N} 条重要更新` |
| `en` | `AI Daily Digest {DATE}` | `{N} notable updates today` |
| `ja` | `AI デイリーダイジェスト {DATE}` | `本日の注目 {N} 件` |

### Emoji Markers by Score

| Score Range | Emoji | Meaning |
|-------------|-------|---------|
| 9-10 | 🔥 | Major / breakthrough |
| 7-8 | ⭐ | Important |
| 5-6 | 🔷 | Notable |

### Item Format

Each item follows this structure:

```
{emoji} **{Entity} {Event description}**
{One to two sentence summary with key metrics, numbers, or specifics.}
```

**Rules:**
- Title is bold, includes entity name + concise event description
- Summary is 1-2 sentences max — condense the raw summary to the most essential information
- Include specific numbers (benchmark scores, parameter counts, pricing, versions) when available
- No score numbers displayed — the emoji conveys importance level
- Items separated by a blank line

### Special Formatting

For GitHub Trending items or items with notable engagement metrics:

```
🔥 **GitHub 热门项目：{repo-name}（Stars 暴涨！）**
⭐ {star_count}(+{delta}) | {one-line description}
```

### Link Placement

**`MESSAGE_LINKS=bottom`** (default — recommended for WeChat, Telegram):

Links grouped as a numbered reference list at the bottom:

```
---
[1] {Entity Event} - {URL}
[2] {Entity Event} - {URL}
```

**`MESSAGE_LINKS=inline`** (for Slack, Discord, rich-text platforms):

Link appended after each item's summary:

```
🔥 **Anthropic 发布 Claude 4.5 Sonnet**
新一代中端模型，编程能力提升18%，200K上下文窗口。
🔗 https://anthropic.com/news/claude-4-5-sonnet
```

### Footer

```
---
Powered by MorningAI | Full report: report_{DATE}.md
```

---

## Image Generation

### When to Generate

Generate `message_{DATE}.png` only if image generation is available (i.e., `IMAGE_GEN_PROVIDER` is configured and not `none`). If unavailable, skip image generation and produce text only.

### Image Specifications

| Property | Value |
|----------|-------|
| Aspect Ratio | 9:16 portrait |
| Layout | Single-column vertical card stack |
| Cards | One card per item, compact format |
| Card Content | Emoji marker + bold title + one-line summary |
| Style | From `MESSAGE_IMAGE_STYLE` or `IMAGE_STYLE` config |

### Image Prompt Template

```
9:16 portrait infographic, {HEADER_TEXT} {YYYY-MM-DD}, ALL text content in {LANG}.
Purpose: Compact message digest for mobile sharing on messaging apps.

Total news items: {N}

News cards (display EXACTLY {N} cards, compact vertical layout):

Card 1: {emoji} {Entity name} {Event description}
- {One-line summary with key metrics}

Card 2: {emoji} {Entity name} {Event description}
- {One-line summary with key metrics}

(... list all {N} items ...)

CRITICAL RULES:
- ALL text on this image MUST be in {LANG}
- Entity names are proper nouns (OpenAI, DeepSeek, Cursor) — keep as-is, do NOT translate
- Each card has: emoji marker + bold title + one-line summary (NOT multi-line bullets)
- Use 🔥 for top items, ⭐ for important items, 🔷 for regular items
- Compact single-column vertical stack — one card below another
- Title font: 18pt bold, summary font: 13pt regular
- Cards separated by thin divider or subtle spacing (12px)
- Card width fills 90% of image width
- Do NOT display score numbers, badges, or importance markers
- Do NOT invent items not listed
- Maximize content area — minimize decorative elements
- Header: "{HEADER_TEXT} {YYYY-MM-DD}" at top
- Footer: small gray text "Powered by MorningAI" at bottom
- Optimized for screenshot sharing in messaging apps

{STYLE_BLOCK}

Message digest layout adaptation:
- Single-column vertical stack (NOT grid layout)
- Each card: title line + summary line only (compact, no multi-line bullets)
- Tight vertical spacing between cards
- Clean, uncluttered, high information density
- Mobile-optimized: large enough text to read on phone screens
```

**Variable substitution:**
- `{HEADER_TEXT}`: See Language-Specific Headers table above
- `{LANG}`: "Chinese" for zh, "English" for en, "Japanese" for ja
- `{STYLE_BLOCK}`: Injected from existing style presets (see `skills/gen-infographic/scripts/styles.py`)

### Image Generation Method

Use the same methods as Step 4 (gen-infographic):

**Option A** — Native tool (if supported):
Generate using built-in image generation capability with the prompt above.

**Option B** — Python script:
```bash
cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --prompt "{prompt}" -o {CWD}/message_{YYYY-MM-DD}.png
```

---

## Workflow Summary

1. Check `MESSAGE_ENABLED=true` — skip if not enabled
2. Read `data_{DATE}.json` from the working directory
3. Read this specification and the digest template (`templates/digest.md`)
4. Select items: filter by score >= `MESSAGE_MIN_SCORE`, sort desc, limit to `MESSAGE_MAX_ITEMS`
5. Generate text digest → write to `{CWD}/message_{DATE}.md`
6. If image generation available → build prompt from template, generate → `{CWD}/message_{DATE}.png`

---

## Example Output

### Chinese (`--lang zh`)

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
Powered by MorningAI | Full report: report_2026-04-08.md
```

### English (`--lang en`)

```
AI Daily Digest 2026-04-08

8 notable updates today

🔥 **Anthropic Releases Claude 4.5 Sonnet**
New mid-tier model with +18% SWE-Bench, 200K context, 40% faster output. Available via API and claude.ai.

⭐ **Google Gemini 2.5 Flash Enters Public Preview**
Flash-tier model with native multimodal reasoning, 1M context. Free tier on AI Studio.

⭐ **Cursor Background Agents Now Generally Available**
Autonomous background agents for multi-file refactoring, test generation, and PR creation. Max 10 concurrent on Pro.

...

---
[1] Anthropic Claude 4.5 Sonnet - https://x.com/AnthropicAI/status/example
[2] Google Gemini 2.5 Flash - https://x.com/GoogleDeepMind/status/example
...

---
Powered by MorningAI | Full report: report_2026-04-08.md
```

---

## Notes

- The text digest reads from `data_{DATE}.json` directly — it does NOT depend on the report being generated first
- All summaries must be condensed to 1-2 sentences — extract the most important facts, numbers, and metrics from the full summary
- Entity names are always preserved as proper nouns regardless of language setting
- The image is optional — if no image generation provider is configured, only the text file is produced
- When `MESSAGE_LINKS=bottom`, the reference numbers are implicit (ordered by item appearance) — do NOT add `[1]` markers in the item body
