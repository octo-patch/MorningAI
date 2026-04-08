---
name: gen-infographic
description: Generate cover and per-type infographics for AI News Daily
---

## Objective

Generate multiple infographics for the daily report:

1. **Cover infographic** — top 4-5 updates across all types
2. **Per-type infographics** — one for each type that has important (7+) items

---

## Output Specs

| Image | Filename | When to generate |
|-------|----------|-----------------|
| Cover | `news_infographic_YYYY-MM-DD.png` | Always (if image gen is enabled) |
| Model | `news_infographic_YYYY-MM-DD_model.png` | Type has 7+ score items |
| Product | `news_infographic_YYYY-MM-DD_product.png` | Type has 7+ score items |
| Benchmark | `news_infographic_YYYY-MM-DD_benchmark.png` | Type has 7+ score items |
| Funding | `news_infographic_YYYY-MM-DD_funding.png` | Type has 7+ score items |

- **Size**: 16:9 landscape
- **Format**: PNG

> **`IMAGE_GEN_TYPES` config**: Controls which per-type images to generate. Default: `auto` (only types with 7+ items). Options: `all` (all types with any items), `none` (cover only), or comma-separated types like `model,product`.

---

## Title Format Specification

Each news title **must include three elements**:

| Element | Description | Example |
|---------|-------------|---------|
| **Entity name** | Company/product/organization name | NVIDIA, Cursor, Midjourney |
| **Event subject** | Specific model/product/event name | Alpamayo, Agent mode, V7 |
| **Core event** | Verb phrase describing the event | releases, open-sources, tops leaderboard, closes funding |

### Title Examples

✅ **Correct Examples**:
- NVIDIA Alpamayo Releases Open-Source Autonomous Driving VLA Model
- Cursor Closes $900M Series B Funding
- Midjourney V7 Officially Launches

❌ **Incorrect Examples**:
- Alpamayo 1 (missing entity name and event)
- NVIDIA Alpamayo (missing event description)
- Open-source autonomous driving model released (missing entity name)

---

## Content Detail Rules

Determine number of points based on score, **but do NOT use `[MAJOR]`/`[MINOR]` tags in Prompt or image**:

| Score | Number of Points | Card Size |
|-------|-----------------|-----------|
| **>= 7** | 3-5 detailed points | Large card (priority display) |
| **< 7** | 2-3 concise points | Small card |

> ⚠️ Score classification is only for guiding content detail level. **Do NOT** use `[MAJOR]`/`[MINOR]` or similar labels in Prompt!

---

## Prompt Template

```
16:9 infographic, AI News Daily {YYYY-MM-DD}, English text content.

Total news items for today: {N}

News cards (display EXACTLY {N} cards):

Card 1: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}
- {Point 3}
- {Point 4}
- {Point 5}

Card 2: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}
- {Point 3}

(... list according to actual item count ...)

CRITICAL RULES:
- Each card title MUST include: Entity name + Event subject + Event description
- Display complete titles, do NOT truncate
- Do NOT display any labels like [MAJOR], [MINOR], or importance markers
- Do NOT invent items not listed
- Display ALL bullet points for each card
- If fewer than 4 items, use more whitespace and decorative elements

Style: Clean editorial magazine layout. Off-white (#F5F5F0) background with subtle warm gray grid lines. Bold sans-serif header "AI News Daily" in black with a vivid accent color underline. Each card is a white rectangle with soft drop shadow (4px blur, 10% black), separated by generous whitespace. Use a refined accent palette: deep navy (#1A2744) for card titles, coral red (#E8553D) for score badges, muted teal (#2A9D8F) for bullet icons, slate gray (#4A5568) for body text. NO gradients, NO textures, NO background patterns — pure flat white space.
Layout: Top row 1-2 large cards (60% height), bottom row 2-3 smaller cards. Cards aligned to a strict grid with equal gutters (24px). Score badge as a bold colored pill in top-right corner of each card.
Card design: Card title in 18pt bold navy sans-serif, subtitle in 12pt gray italic. Bullet points with small teal dot markers, 14pt regular weight. Thin 1px light gray top-border on each card for subtle separation. NO icons, NO illustrations, NO decorative elements inside cards — text only with strong typographic hierarchy.
```

---

## Usage Instructions

### 1. Determine Images to Generate

From the report, identify:
- **Cover**: Top 4-5 items across all types by score
- **Per-type**: For each type (Model/Product/Benchmark/Funding), check if it has 7+ score items. If yes, generate a per-type image.

### 2. Build Prompts

**Cover prompt**: Use the Cover Prompt Template above.

**Per-type prompt**: Use the Per-Type Prompt Template below.

### Per-Type Prompt Template

```
16:9 infographic, AI News Daily {YYYY-MM-DD} — {Type} Updates, English text content.

Total news items: {N}

News cards (display EXACTLY {N} cards):

Card 1: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}
- {Point 3}

Card 2: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}

(... list according to actual item count ...)

CRITICAL RULES:
- Each card title MUST include: Entity name + Event subject + Event description
- Display complete titles, do NOT truncate
- Do NOT display any labels like [MAJOR], [MINOR], or importance markers
- Do NOT invent items not listed
- Display ALL bullet points for each card
- If fewer than 3 items, use more whitespace and decorative elements

Style: Clean editorial magazine layout. Off-white (#F5F5F0) background with subtle warm gray grid lines. Bold sans-serif header "AI News Daily — {Type} Updates" in black with a vivid accent color underline. Each card is a white rectangle with soft drop shadow (4px blur, 10% black), separated by generous whitespace. Use a refined accent palette: deep navy (#1A2744) for card titles, coral red (#E8553D) for score badges, muted teal (#2A9D8F) for bullet icons, slate gray (#4A5568) for body text. NO gradients, NO textures, NO background patterns — pure flat white space.
Layout: Cards arranged in grid layout. Cards aligned with equal gutters (24px). Score badge as a bold colored pill in top-right corner of each card.
Card design: Card title in 18pt bold navy sans-serif, subtitle in 12pt gray italic. Bullet points with small teal dot markers, 14pt regular weight. Thin 1px light gray top-border on each card for subtle separation. NO icons, NO illustrations, NO decorative elements inside cards — text only with strong typographic hierarchy.
```

### 3. Generate Images

**Option A** — Native tool (if supported):
Generate each image using your tool's built-in capability.

**Option B** — Python script (batch mode):
Build a manifest JSON and run once:

```bash
# Create manifest.json with all prompts
cat > manifest.json << 'MANIFEST'
[
  {"prompt": "<cover prompt>", "output": "news_infographic_YYYY-MM-DD.png"},
  {"prompt": "<model prompt>", "output": "news_infographic_YYYY-MM-DD_model.png"},
  {"prompt": "<product prompt>", "output": "news_infographic_YYYY-MM-DD_product.png"}
]
MANIFEST

cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/manifest.json
```

### 4. Post-generation Verification (required)

For each generated image:
- Check card count equals N
- Verify each card title includes complete three elements
- Check if titles are truncated
- Confirm no unprovided content
- Confirm no `[MAJOR]`, `[MINOR]` or similar labels displayed
- If issues found, regenerate or manually correct

### 5. Insert into Report

- Cover image: at report beginning
- Per-type images: at the top of each type section

---

## Handling Few Updates

When valid news items < 4, **do NOT pad with fake content**:

| Item Count | Layout Strategy |
|------------|----------------|
| **1 item** | Centered large card + "Today's Highlight" label + whitespace and decorative elements |
| **2 items** | Left-right symmetric or top-bottom stacked |
| **3 items** | Three-column even or pyramid layout |
| **4-5 items** | Standard grid layout |

> **Core principle**: prefer whitespace over fabrication.

---

## Notes

- Title uses "AI News Daily", news content in English
- **Strictly generate based on actual item count**, do not force 4-5 items
- **Do NOT use `[MAJOR]`/`[MINOR]` labels in Prompt**
- Use card size and point count to reflect importance differences
- Insert image into report Markdown beginning after generation
- **Popular Model Blocklist**: unless explicitly in report, do not include models/products not in the report
