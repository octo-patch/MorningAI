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

| Image | Filename | When to generate | Aspect |
|-------|----------|-----------------|--------|
| Cover | `news_infographic_YYYY-MM-DD.png` | Always (if image gen is enabled) | 16:9 |
| Model | `news_infographic_YYYY-MM-DD_model.png` | Type has 7+ score items | 16:9 (standalone) or 9:16 (long image) |
| Product | `news_infographic_YYYY-MM-DD_product.png` | Type has 7+ score items | 16:9 (standalone) or 9:16 (long image) |
| Benchmark | `news_infographic_YYYY-MM-DD_benchmark.png` | Type has 7+ score items | 16:9 (standalone) or 9:16 (long image) |
| Funding | `news_infographic_YYYY-MM-DD_funding.png` | Type has 7+ score items | 16:9 (standalone) or 9:16 (long image) |
| Combined | `news_infographic_YYYY-MM-DD_combined.png` | Sparse mode or `--stitch` output | 9:16 |

- **Default format**: 16:9 landscape PNG (standalone mode)
- **Long image format**: 9:16 portrait PNG for sections, stitched into a vertical long image
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

## Style Presets

Select a visual style via `IMAGE_STYLE` config (default: `classic`). Insert the matching style block into `{STYLE_BLOCK}` in all prompt templates below.

### `classic` — Clean Editorial Magazine

```
Style: Clean editorial magazine layout. Off-white (#F5F5F0) background with subtle warm gray grid lines. Bold sans-serif header "AI News Daily" in black with a vivid accent color underline. Each card is a white rectangle with soft drop shadow (4px blur, 10% black), separated by generous whitespace. Use a refined accent palette: deep navy (#1A2744) for card titles, coral red (#E8553D) for score badges, muted teal (#2A9D8F) for bullet icons, slate gray (#4A5568) for body text. NO gradients, NO textures, NO background patterns — pure flat white space.
Layout: Top row 1-2 large cards (60% height), bottom row 2-3 smaller cards. Cards aligned to a strict grid with equal gutters (24px). Score badge as a bold colored pill in top-right corner of each card.
Card design: Card title in 18pt bold navy sans-serif, subtitle in 12pt gray italic. Bullet points with small teal dot markers, 14pt regular weight. Thin 1px light gray top-border on each card for subtle separation. NO icons, NO illustrations, NO decorative elements inside cards — text only with strong typographic hierarchy.
```

### `dark` — Dark Mode

```
Style: Dark mode editorial layout. Deep charcoal (#1A1A2E) background. Bold sans-serif header "AI News Daily" in white (#FAFAFA) with electric blue (#00D4FF) accent underline. Each card is a dark slate (#16213E) rectangle with subtle 1px border in muted blue (#0F3460), separated by generous spacing. Accent palette: white (#FAFAFA) for card titles, electric blue (#00D4FF) for score badges, soft violet (#7B68EE) for bullet icons, light gray (#B0BEC5) for body text. NO gradients, NO glow effects — clean flat dark surfaces.
Layout: Top row 1-2 large cards (60% height), bottom row 2-3 smaller cards. Cards aligned to a strict grid with equal gutters (24px). Score badge as a bold colored pill in top-right corner of each card.
Card design: Card title in 18pt bold white sans-serif, subtitle in 12pt light gray italic. Bullet points with small violet dot markers, 14pt regular weight. Thin 1px muted blue top-border on each card. NO icons, NO illustrations — text only with strong typographic hierarchy on dark background.
```

### `glassmorphism` — Frosted Glass

```
Style: Glassmorphism editorial layout. Soft gradient background blending from lavender (#E8EAF6) top-left to pale rose (#FCE4EC) bottom-right. Bold sans-serif header "AI News Daily" in dark charcoal (#212121) with warm coral (#FF6B6B) accent underline. Each card is a semi-transparent frosted white panel (rgba(255,255,255,0.65)) with backdrop blur effect, rounded corners (16px), and subtle white border (1px, 30% opacity). Accent palette: charcoal (#212121) for card titles, warm coral (#FF6B6B) for score badges, soft indigo (#5C6BC0) for bullet icons, medium gray (#546E7A) for body text. Soft diffused shadows (8px blur, 5% black) behind each card.
Layout: Top row 1-2 large cards (60% height), bottom row 2-3 smaller cards. Cards aligned to a grid with generous gutters (28px). Score badge as a rounded pill with slight glass effect in top-right corner.
Card design: Card title in 18pt bold charcoal sans-serif, subtitle in 12pt gray italic. Bullet points with small indigo dot markers, 14pt regular weight. NO hard borders — rely on frosted glass contrast for separation. Clean, airy, modern feel.
```

### `newspaper` — Classic Newsprint

```
Style: Classic newspaper editorial layout. Warm cream (#FFF8E7) background with very faint paper texture grain. Bold serif header "AI News Daily" in deep black (#1A1A1A) with crimson red (#B71C1C) thin rule line below. Each card is separated by thin black hairline rules (1px) — NO card backgrounds, NO shadows, NO boxes. Content flows in a column-based newspaper grid. Accent palette: deep black (#1A1A1A) for card titles in bold serif, crimson (#B71C1C) for score indicators as small circled numbers, dark gray (#333333) for bullet text in serif, medium gray (#666666) for subtitles in italic serif.
Layout: Multi-column newspaper grid (2-3 columns). Large stories span full width at top, smaller stories in side-by-side columns below. Separated by horizontal and vertical hairline rules. NO cards, NO boxes — pure typographic layout.
Card design: Card title in 18pt bold black serif, subtitle in 12pt gray italic serif. Bullet points with small em-dash markers, 14pt regular serif weight. Dateline-style score indicator. Feels like the front page of a prestigious broadsheet.
```

### `tech` — Terminal / Hacker

```
Style: Tech terminal aesthetic layout. Near-black background (#0D1117) with very faint dot grid pattern (8px spacing, 5% white). Bold monospace header "AI News Daily" in bright cyan (#00FFCC) with a blinking cursor underscore effect. Each card is a dark panel (#161B22) with 1px border in dim cyan (#1A3A3A), rounded corners (4px). Accent palette: bright green (#39FF14) for card titles in monospace bold, electric cyan (#00FFCC) for score badges formatted as `[8.5]`, amber (#FFB000) for bullet markers as `>` symbols, light gray (#C9D1D9) for body text in monospace. Each card has a subtle top-left label like `// MODEL` or `// PRODUCT` in dim green (#1A4A1A).
Layout: Top row 1-2 large cards (60% height), bottom row 2-3 smaller cards. Cards aligned to a strict grid with equal gutters (16px). Compact spacing, information-dense.
Card design: Card title in 16pt bold green monospace, subtitle in 11pt gray monospace. Bullet points with amber `>` markers, 13pt regular monospace. Thin 1px dim cyan border. Feels like a developer dashboard or terminal readout.
```

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

{STYLE_BLOCK}
```

**`{STYLE_BLOCK}`** — insert the matching style block from the Style Presets section above, based on `IMAGE_STYLE` config (default: `classic`).

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

{STYLE_BLOCK}
```

> Adjust the style header text to "AI News Daily — {Type} Updates" when using the preset.

### Section Prompt Template (Long Image Mode)

Use this template for per-type section images when generating a long image (`--stitch` mode). These are designed as SECTIONS of a vertical composition, NOT standalone images.

```
9:16 portrait infographic section, {Type} Updates {YYYY-MM-DD}, English text content.

Total news items: {N}

News cards (display EXACTLY {N} cards, arranged vertically):

Card 1: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}
- {Point 3}

Card 2: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}

(... list according to actual item count ...)

CRITICAL RULES:
- This is a SECTION of a longer image — do NOT include "AI News Daily" header or top branding
- Start with a section header: "{Type} Updates" in navy (#1A2744) with coral (#E8553D) underline
- Cards arranged vertically (portrait layout), one below another
- Each card title MUST include: Entity name + Event subject + Event description
- Display complete titles, do NOT truncate
- Do NOT display any labels like [MAJOR], [MINOR], or importance markers
- Do NOT invent items not listed
- Display ALL bullet points for each card

{STYLE_BLOCK}
```

> For section images: omit the "AI News Daily" top header; start with a section header "{Type} Updates" instead. Adapt the preset's colors for section headers accordingly.

### Combined Prompt Template (Sparse Content)

Use when total qualifying items across all types is **8 or fewer**. Produces a single self-contained 9:16 portrait image with all content — no stitching needed.

```
9:16 portrait infographic, AI News Daily {YYYY-MM-DD}, English text content.

Total news items: {N}

{For each active type with items, include a labeled section:}

--- {Type} Updates ---

Card 1: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}

(... cards for this type ...)

{Next type section...}

CRITICAL RULES:
- Header: "AI News Daily {YYYY-MM-DD}" at top, with branding
- Each type section has a colored section divider with the type name
- Cards arranged vertically within each section
- Each card title MUST include: Entity name + Event subject + Event description
- Use generous whitespace — do NOT compress cards to fill space
- If only 1-2 types have items, center content vertically
- Do NOT invent items not listed

{STYLE_BLOCK}
```

> For combined images: include "AI News Daily" header and type section dividers. Adapt the preset's colors for section dividers accordingly.

---

## Long Image Strategy

When generating images for a shareable long image, use the adaptive strategy below instead of the default standalone mode.

### Decision Logic

| Condition | Strategy | What to generate |
|-----------|----------|-----------------|
| Total qualifying items ≤ 8 | **Sparse** | 1 combined image (9:16, Combined Template) |
| Total qualifying items > 8 | **Normal** | Cover (16:9) + section images per active type (9:16, Section Template), then `--stitch` |

"Qualifying items" = items that would appear in any infographic (7+ score for per-type, top 4-5 for cover).

### Sparse Strategy

- Use the **Combined Prompt Template**
- Set `"aspect_ratio": "9:16"` in manifest
- Do **NOT** use `--stitch` (single image, no stitching needed)
- Output: `news_infographic_YYYY-MM-DD_combined.png`

### Normal Strategy

- **Cover**: standard Cover Prompt Template, aspect `"16:9"`
- **Sections**: use **Section Prompt Template** (NOT Per-Type Template) with `"aspect_ratio": "9:16"` — these omit "AI News Daily" branding since the cover already has it
- Use `--stitch` to combine into a single long image
- Manifest example:
  ```json
  [
    {"prompt": "<cover prompt>", "output": "news_infographic_YYYY-MM-DD.png"},
    {"prompt": "<model section>", "output": "news_infographic_YYYY-MM-DD_model.png", "aspect_ratio": "9:16"},
    {"prompt": "<product section>", "output": "news_infographic_YYYY-MM-DD_product.png", "aspect_ratio": "9:16"}
  ]
  ```

### Default (Non-Long-Image) Mode

Use the existing Cover Prompt Template and Per-Type Prompt Template with 16:9 aspect ratio. This is unchanged.

---

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

**Option C** — Long image for social sharing (sparse mode, single combined image):
```bash
cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/manifest.json
```
> Use the Combined Prompt Template with `"aspect_ratio": "9:16"` in manifest. No `--stitch` needed.

**Option D** — Long image for social sharing (normal mode, cover + sections stitched):
```bash
cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/manifest.json --stitch
```
> Use Cover Template (16:9) + Section Templates (9:16). Requires `pip install Pillow`. Produces `news_infographic_YYYY-MM-DD_combined.png`.

> See **Long Image Strategy** section above for when to use Option C vs D.

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
