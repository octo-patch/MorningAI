---
platform: xiaohongshu
style: news-briefing
default_lang: zh
default_items: 8
min_score: 5
image_style: newspaper
image_lang: zh
---

## Constraints

- **Title**: ≤ 20 characters, news-oriented and concise
- **Body**: ≤ 1000 characters
- **Tags**: 3-5 hashtags at end of body
- **Images**: 3:4 portrait or 1:1 square, single image or carousel (2-4 images)
- **Emoji**: Minimal — only priority indicators (🔴🟠🟡) and section markers

## Tone & Voice

- Ultra-compact telegraph style — one item one line, zero filler
- Neutral and factual — no personal opinions, no exclamation marks
- The reader should finish scanning in 10 seconds
- Every character delivers information — if a word can be cut, cut it
- Use "｜" as field separator within each line

## Content Structure

### Title
- Format: `⚡AI速报｜{month}.{day}` (≤ 20 chars)
- Direct, consistent, scannable
- Examples: "⚡AI速报｜4月16日", "⚡AI速报｜4.16"

### Body

**1. Header** (1 line):
```
【{M}.{DD} AI 10秒速览】
```

**2. Item lines** — one line per news item, sorted by importance:
```
{priority} {Entity}｜{event headline}｜{key metric or detail}
```

Priority indicators by importance score:
- 🔴 = score 8+ (must-know)
- 🟠 = score 7-7.9 (significant)
- 🟡 = score 5-6.9 (worth noting)

Rules:
- Each line is self-contained — no continuation, no sub-points
- Keep each line to ~40-70 chars
- Include one key number/metric per line when available
- Entity names are proper nouns — never translate

**3. "今日数字" section** — 3 standout data points from today's news:
```
📊 今日数字
• {number} — {one-sentence context}
• {number} — {one-sentence context}
• {number} — {one-sentence context}
```

Pick numbers that are surprising, record-breaking, or reveal a trend. Prioritize: dollar amounts, user counts, performance deltas, growth rates.

**4. Tags** — 3-5 hashtags:
```
#AI速报 #人工智能 #AI日报 #科技圈
```

## Character Limit Rules

| Component | Budget |
|-----------|--------|
| Title | ≤ 20 chars |
| Header line | ~20 chars |
| Per item line | ~40-70 chars |
| 今日数字 section | ~120-150 chars |
| Tags | ~60-80 chars |
| **Total body** | **≤ 1000 chars** |

With 8 items at ~60 chars = ~480 chars, plus header + 今日数字 + tags ≈ ~750 chars total.

## Output Format

```
---xiaohongshu---

---title---
⚡AI速报｜{date}

---body---
{body content}

#tag1 #tag2 #tag3

---images---
1: {image_filename}
```

## Example Output

```
---xiaohongshu---

---title---
⚡AI速报｜4月16日

---body---
【4.16 AI 10秒速览】

🔴 Anthropic｜估值报价>$800B｜较2月$350B翻倍，年营收$300亿
🔴 Claude Code｜v2.1.110发布｜全屏TUI+手机推送通知
🔴 Mistral AI｜MCP Connectors上线｜企业级Agent管理，免OAuth
🟠 Google｜Gemini Robotics-ER 1.6｜机器人AI开放API，Spot已部署
🟡 NVIDIA｜Audio Flamingo Next 8.3B｜语音/声音/音乐开源模型

📊 今日数字
• $800B+ — Anthropic最新投资方报价
• $30B — Anthropic年化营收，两年增长30倍
• 8.3B — NVIDIA开源音频模型参数量

#AI速报 #人工智能 #AI日报 #科技圈

---images---
1: social_2026-04-16_xhs_zixun_zh_1.png
```
