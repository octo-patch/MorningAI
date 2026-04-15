---
name: gen-social
version: "1.2.8"
description: Generate platform-specific social media copy and images for content distribution
---

## Objective

Transform the daily AI news report into platform-optimized social media content. Generates ready-to-post copy and adapted images for multiple platforms, with support for multiple accounts and styles per platform.

**Phase 1 scope**: Generate copy files + images. No auto-publish (future phase).

---

## Supported Platforms

### X / Twitter

| Constraint | Value |
|------------|-------|
| Single tweet | 280 characters max |
| Thread | Unlimited tweets (recommended 5-15) |
| Images per tweet | Up to 4, 16:9 or 1:1 |
| Hashtags | 2-3 per tweet |
| Mentions | @handle format |

### Xiaohongshu (Little Red Book)

| Constraint | Value |
|------------|-------|
| Title | 20 characters max |
| Body | 1000 characters max |
| Images | Up to 9 per post, 3:4 or 1:1 (carousel) |
| Tags | 5-10 # tags at end of body |
| Emoji | Heavy use expected (platform culture) |

---

## Style Definitions

### Custom Personas & Styles

Templates define the voice, tone, and format for each channel. This repo ships with **one example template per platform** as a starting point:

- **X**: `templates/x/insider.md` (Tech Insider persona)
- **Xiaohongshu**: `templates/xiaohongshu/educational.md` (科普体)

To create your own persona or style:

```bash
# X persona
cp skills/gen-social/templates/x/insider.md skills/gen-social/templates/x/my-persona.md

# Xiaohongshu style
cp skills/gen-social/templates/xiaohongshu/educational.md skills/gen-social/templates/xiaohongshu/my-style.md
```

Edit the copy, then set your channel config `style` field to match the filename (e.g. `"style": "my-persona"`). Custom templates in these directories are gitignored — your personas stay local.

### X Styles

Each X style has a distinct **persona** — a consistent voice and perspective that makes the account feel like a real person, not a news feed.

**Included example:**

| Style | Persona | Template | Tone | Default Items | Min Score |
|-------|---------|----------|------|---------------|-----------|
| `insider` | Tech Insider | `templates/x/insider.md` | Industry insider, dry humor, connects dots | 3 | 7 |

**Create your own** — some persona directions to consider:

| Persona Direction | Tone | Reference |
|-------------------|------|-----------|
| Hype-Free Analyst | Data-driven, measured, pattern recognition | @Benedict Evans |
| Builder | Practical, opinionated, "I tried it" | @levelsio |
| Witty Commentator | Sharp, meme-aware, short punchy takes | Tech Twitter culture |

### Xiaohongshu Styles

**Included example:**

| Style | Template | Tone | Default Items | Min Score |
|-------|----------|------|---------------|-----------|
| `educational` | `templates/xiaohongshu/educational.md` | Structured explainer, numbered | 3-5 | 6 |

**Create your own** — some style directions to consider:

| Style Direction | Tone | Key Traits |
|-----------------|------|------------|
| 种草体 (Recommendation) | Enthusiastic discovery, "must see!" | Heavy emoji, excitement, personal voice |
| 资讯体 (News Briefing) | Concise bullet list, high info density | Compact, neutral, professional |

---

## Channel Configuration

A **channel** is the core abstraction: one channel = one platform + one style + one language + content selection rules. Each channel produces an independent set of output files.

### Channel Config File

Located at `~/.config/morning-ai/social_channels.json` (or path set via `SOCIAL_CHANNELS_FILE`).

```json
[
  {
    "id": "x_insider_en",
    "platform": "x",
    "style": "insider",
    "lang": "en",
    "items": 3,
    "min_score": 7,
    "image": true,
    "image_aspect": "16:9"
  },
  {
    "id": "x_thread_en",
    "platform": "x",
    "style": "thread",
    "lang": "en",
    "items": 5,
    "min_score": 6,
    "image": true,
    "image_aspect": "16:9"
  },
  {
    "id": "xhs_kepu_zh",
    "platform": "xiaohongshu",
    "style": "educational",
    "lang": "zh",
    "items": 5,
    "min_score": 6,
    "image": true,
    "image_aspect": "3:4",
    "image_count": 4
  },
  {
    "id": "xhs_zhongcao_zh",
    "platform": "xiaohongshu",
    "style": "recommendation",
    "lang": "zh",
    "items": 3,
    "min_score": 7,
    "image": true,
    "image_aspect": "3:4",
    "image_count": 3
  }
]
```

### Channel Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique channel identifier, used in output filenames |
| `platform` | string | Yes | `x` or `xiaohongshu` |
| `style` | string | Yes | Style name (see Style Definitions above) |
| `lang` | string | Yes | Language code: `en`, `zh`, `ja`, etc. |
| `items` | number | No | Max items to include (default: from template) |
| `min_score` | number | No | Minimum score threshold (default: from template) |
| `image` | boolean | No | Generate images for this channel (default: `false`) |
| `image_aspect` | string | No | Image aspect ratio: `16:9`, `1:1`, `3:4` (default: platform default) |
| `image_count` | number | No | Number of carousel images for xiaohongshu (default: 1) |
| `image_style` | string | No | Override image style: `classic`, `dark`, `glassmorphism`, `newspaper`, `tech` (default: persona's recommended style) |
| `include_types` | array | No | Filter by content types, e.g. `["model", "product"]` (default: all) |

### Quick Setup (Single Channel via Env Vars)

When only one channel is needed, use env vars instead of a JSON file:

```bash
SOCIAL_PLATFORM=x
SOCIAL_STYLE=insider
SOCIAL_LANG=en
```

This creates a single channel with id `{platform}_{style}_{lang}`.

---

## Content Selection Rules

For each channel, select items from the daily report data:

1. **Filter by score**: only items with `importance >= min_score`
2. **Filter by type**: if `include_types` is set, only those content types
3. **Sort by score**: highest first
4. **Limit**: take top N items (from channel `items` setting or template default)
5. **Translate**: if source data language differs from channel `lang`, translate content. Entity names (proper nouns) stay unchanged.

---

## Copy Generation

For each channel:

1. Read the template: `{SKILL_DIR}/skills/gen-social/templates/{platform}/{style}.md`
2. Select items using Content Selection Rules above
3. Generate copy following the template's format rules, character limits, and tone
4. Validate character counts against platform limits

### Post-Generation Checklist

- [ ] Character count within platform limits (280/tweet for X, 20 title + 1000 body for Xiaohongshu)
- [ ] Language matches channel `lang` setting
- [ ] Entity names preserved as proper nouns (not translated)
- [ ] Source links included where template requires them
- [ ] Hashtags/tags present and relevant
- [ ] No score numbers displayed in copy (scores are internal only)

---

## Image Generation

Social images reuse the existing image generation infrastructure (`lib/image_gen.py`) and the same providers (Gemini/GPT/MiniMax).

### Image Language Rules

Image text language **must match the target platform**, not the report source language:

| Platform | Image Language | Header Text |
|----------|---------------|-------------|
| **X** | **English only** | "MorningAI" |
| **Xiaohongshu** | **Chinese only** | "MorningAI" |

All card titles, bullet points, section headers, and any text rendered on the image must be in the platform's language. Entity names (proper nouns like OpenAI, DeepSeek) remain unchanged.

### Persona–Image Style Mapping

Each persona/style has a **recommended image style** that matches its voice. This overrides the global `IMAGE_STYLE` setting for social images.

#### X Styles

| Persona | Recommended Image Style | Why |
|---------|------------------------|-----|
| **insider** (Tech Insider) | `tech` | Terminal aesthetic matches the insider/hacker vibe — monospace, cyan/green, dark background |
| **thread** (Hype-Free Analyst) | `classic` | Clean editorial magazine — serious, data-focused, no visual noise |
| **commentary** (Builder) | `dark` | Bold dark mode with electric blue — confident, modern, stands out in timeline |

#### Xiaohongshu Styles

| Style | Recommended Image Style | Why |
|-------|------------------------|-----|
| **recommendation** (种草体) | `glassmorphism` | Frosted glass, warm tones — matches the lifestyle/discovery aesthetic of 种草 content |
| **educational** (科普体) | `classic` | Clean editorial — matches structured, authoritative educational content |
| **news-briefing** (资讯体) | `newspaper` | Classic newsprint — information-dense, professional, matches compact news format |

The recommended style is a default — channels can override via `image_style` field in the channel config. If not set, the persona's recommended style is used. If no persona mapping exists, falls back to the global `IMAGE_STYLE` setting.

### Platform-Specific Image Adaptation

**X images**:
- Aspect ratio: 16:9 (landscape) or 1:1 (square)
- **All text in English** — titles, bullets, headers, everything
- Header: "MorningAI"
- Apply the persona's recommended image style (see mapping above)
- Single image per tweet (or up to 4 for threads)

**Xiaohongshu images**:
- Aspect ratio: 3:4 (portrait) or 1:1 (square)
- **All text in Chinese** — titles, bullets, headers, everything
- Header: "MorningAI"
- Apply the style's recommended image style (see mapping above), plus Xiaohongshu-specific adaptations:
  - Larger font sizes for mobile readability
  - Rounded card corners (16px)
  - Emoji-style bullet markers
- Carousel strategy (when `image_count > 1`):
  - Image 1: Cover overview — top headlines, eye-catching title
  - Image 2-N: Detail pages — 1-2 items per image with expanded bullet points
  - Last image: Follow/subscribe CTA (optional)

### Image Prompt Template

```
{ASPECT} infographic, {HEADER_TEXT} {YYYY-MM-DD}, ALL text content in {LANG}.
Platform: {PLATFORM}

Total news items: {N}

News cards (display EXACTLY {N} cards):

Card 1: {Entity name} {Event subject} {Core event verb phrase}
- {Point 1}
- {Point 2}
- {Point 3}

(... list according to actual item count ...)

CRITICAL RULES:
- ALL text on this image MUST be in {LANG} — titles, bullet points, headers, labels, everything
- Entity names are proper nouns (OpenAI, DeepSeek, Cursor) — keep as-is, do NOT translate
- Header text: "{HEADER_TEXT}"
- Each card title MUST include: Entity name + Event subject + Event description
- Display complete titles, do NOT truncate
- Do NOT display score numbers, score badges, or importance markers
- Do NOT invent items not listed
- Display ALL bullet points for each card
- Maximize content area — card titles and bullet points are the primary focus

{STYLE_BLOCK}
{PLATFORM_STYLE_ADDON}
```

**Variable substitution:**
- `{HEADER_TEXT}` → "MorningAI" for X, "MorningAI" for Xiaohongshu
- `{LANG}` → "English" for X, "Chinese" for Xiaohongshu
- `{STYLE_BLOCK}` → from the persona's recommended image style (see `skills/gen-infographic/SKILL.md` Style Presets)

**`{PLATFORM_STYLE_ADDON}`** for Xiaohongshu (append to any base style):
```
Additional Xiaohongshu adaptation:
- ALL text must be in Chinese (except entity proper nouns)
- Use rounded corners (16px) on all cards
- Larger title font (22pt bold) for mobile readability
- Warm accent colors: coral (#FF6B6B), soft pink (#FFB4B4), lavender (#E8EAF6)
- Emoji bullet markers (colored dots or sparkle symbols)
- Clean, fresh, lifestyle-magazine aesthetic
- Generous padding and line spacing for mobile screens
```

**`{PLATFORM_STYLE_ADDON}`** for X (append to any base style):
```
Additional X/Twitter adaptation:
- ALL text must be in English (except entity proper nouns)
- Optimized for timeline scroll — key info visible at small preview size
- High contrast text for readability on mobile
```

### Generating Images

Use the same methods as Step 4 (gen-infographic):

**Option A** — Native tool (if supported):
Generate each image using built-in image generation capability.

**Option B** — Python script batch mode:
Build a manifest JSON and run:
```bash
cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/social/manifest_images.json
```

Manifest entries support `"aspect_ratio": "3:4"` for Xiaohongshu images.

---

## Output Files

All output goes to `{CWD}/social/` directory.

### Naming Convention

```
social/
├── social_{DATE}_{channel_id}.md              # Copy file
├── social_{DATE}_{channel_id}_cover.png       # Single/cover image
├── social_{DATE}_{channel_id}_{N}.png         # Carousel image N
└── social_{DATE}_manifest.json                # Output index
```

### Manifest Format

```json
{
  "date": "2026-04-14",
  "channels": [
    {
      "id": "x_insider_en",
      "platform": "x",
      "style": "insider",
      "lang": "en",
      "copy_file": "social_2026-04-14_x_insider_en.md",
      "images": ["social_2026-04-14_x_insider_en_cover.png"],
      "items_used": 3
    },
    {
      "id": "xhs_kepu_zh",
      "platform": "xiaohongshu",
      "style": "educational",
      "lang": "zh",
      "copy_file": "social_2026-04-14_xhs_kepu_zh.md",
      "images": [
        "social_2026-04-14_xhs_kepu_zh_1.png",
        "social_2026-04-14_xhs_kepu_zh_2.png",
        "social_2026-04-14_xhs_kepu_zh_3.png",
        "social_2026-04-14_xhs_kepu_zh_4.png"
      ],
      "items_used": 5
    }
  ]
}
```

---

## Workflow Summary

1. Check if social content is enabled (`SOCIAL_ENABLED=true`)
2. Load channel configuration (JSON file or env vars)
3. For each channel:
   a. Read the channel's template file
   b. Select top items from report data (score filter + item limit)
   c. Generate copy following template rules and character limits
   d. Write copy to `social/{DATE}_{channel_id}.md`
   e. If `image: true` — build image prompts and generate platform-adapted images
   f. Write images to `social/{DATE}_{channel_id}_{N}.png`
4. Write manifest to `social/{DATE}_manifest.json`

---

## Notes

- Channels are fully independent — each reads from the same daily data but produces separate output
- Multiple channels can target the same platform with different styles, languages, or content focus
- **Image language follows the platform**: X images are always English, Xiaohongshu images are always Chinese — regardless of the channel `lang` setting for copy
- **Image style follows the persona**: each persona/style has a recommended image style that matches its voice (see Persona–Image Style Mapping). Channels can override via `image_style` field
- All content must respect platform character limits — validation is mandatory
- Entity names are proper nouns and must NOT be translated regardless of `lang` setting
- When the same item appears in multiple channels, each channel generates its own adapted version independently
