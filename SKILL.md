---
name: morning-ai
version: "1.0.0"
description: "Daily-scheduled AI news tracker. Collects updates from 76+ AI entities across 9 sources every 24 hours (default 08:00 UTC+8). Generates scored, deduplicated Markdown reports. Supports unattended cron/scheduled execution with date-stamped idempotent output."
argument-hint: 'morning-ai, morning-ai --exclude Funding, morning-ai --depth deep, morning-ai --schedule "0 9 * * *"'
allowed-tools: Bash, Read, Write, Edit, WebSearch
homepage: https://github.com/octo-patch/MorningAI
repository: https://github.com/octo-patch/MorningAI
author: octo-patch
license: MIT
user-invocable: true
schedule:
  frequency: daily
  default-cron: "0 8 * * *"
  timezone: "Asia/Shanghai"
  idempotent: true
  unattended: true
  estimated-duration: "2-5min"
metadata:
  openclaw:
    emoji: "📰"
    requires:
      env:
        - SCRAPECREATORS_API_KEY
      optionalEnv:
        - GITHUB_TOKEN
        - YOUTUBE_API_KEY
        - DISCORD_TOKEN
        - BRAVE_API_KEY
        - EXA_API_KEY
      bins:
        - python3
    primaryEnv: SCRAPECREATORS_API_KEY
    files:
      - "skills/*/scripts/collect.py"
      - "skills/*/scripts/gen_infographic.py"
      - "lib/*"
    homepage: https://github.com/octo-patch/MorningAI
    tags:
      - ai
      - news
      - tracking
      - daily-report
      - model
      - product
      - benchmark
      - funding
      - multi-source
      - scheduled
      - cron
      - automated
      - unattended
      - ai-skill
      - clawhub
---

# morning-ai: AI News Daily Report Generator

> **Permissions overview:** Collects public data from X/Twitter, Reddit, Hacker News, GitHub, HuggingFace, arXiv, YouTube, Discord, and web search. Requires API keys configured in `.env` or `~/.config/morning-ai/.env`. Writes report files to the current working directory. See [Configuration](#configuration) for details.

Track 76+ AI entities across 9 data sources. Collect updates from the past 24 hours, score and deduplicate them, and generate a structured Markdown daily report. Covers 4 types: **Product** (feature launches, version releases), **Model** (new models, open-source weights), **Benchmark** (leaderboard changes, papers), **Funding** (rounds, acquisitions, milestones).

---

## Step 0: Configuration Check

**Before first run, check if the configuration is ready.**

1. Check if `~/.config/morning-ai/.env` or `.env` exists in the skill directory
2. If neither exists, guide the user to set up API keys:

```
Required:
  SCRAPECREATORS_API_KEY  — X/Twitter data collection (get at scrapecreators.com)

Optional (unlock more sources):
  GITHUB_TOKEN            — GitHub releases and repos
  YOUTUBE_API_KEY         — YouTube channel content
  DISCORD_TOKEN           — Discord announcement channels
  BRAVE_API_KEY           — Brave web search
  EXA_API_KEY             — Exa web search

Image generation (for cover infographic, optional):
  IMAGE_GEN_PROVIDER      — Provider: gemini | gpt | minimax | none (default: none)
  IMAGE_STYLE             — Visual style: classic | dark | glassmorphism | newspaper | tech (default: classic)
  GEMINI_API_KEY          — Google Gemini/Imagen API key
  OPENAI_API_KEY          — OpenAI API key (for gpt-image-1)
  MINIMAX_API_KEY         — MiniMax API key
  MINIMAX_API_REGION      — MiniMax region: intl (default) | cn (国内)
```

3. Write the keys to `~/.config/morning-ai/.env` in `KEY=value` format
4. Without any API keys, the following free sources still work: **Reddit** (public JSON), **Hacker News** (Algolia API), **HuggingFace** (public API), **arXiv** (public API)

---

## Step 1: Data Collection

Run the Python collector to gather data from all available sources:

```bash
cd {SKILL_DIR} && python3 skills/tracking-list/scripts/collect.py --date {YYYY-MM-DD} --depth default -o {CWD}/data_{YYYY-MM-DD}.json
```

**Parameters:**
- `--date`: Target date, default today (YYYY-MM-DD)
- `--depth`: Collection depth — `quick` (fast, fewer results), `default`, or `deep` (comprehensive)
- `--sources`: Specific sources only, e.g. `--sources reddit hackernews github`
- `-o`: Output JSON file path

**What it does:**
- Runs 9 collectors concurrently (X, Reddit, HN, GitHub, HuggingFace, arXiv, web, YouTube, Discord)
- Time window: `[Yesterday 08:00, Today 08:00) UTC+8`
- Pipeline: collect → score (1-10) → deduplicate → cross-source link → verification bonus
- Returns structured JSON with all items, stats, and collection metadata

**Timeout:** Allow up to 3 minutes for default depth, 5 minutes for deep.

If the user provides `--exclude` types (e.g. `--exclude Funding`), note which types to filter out in Step 3.

---

## Step 2: Read Specifications

After data collection completes, read the tracking specification to understand scoring criteria, record format, and timeliness rules:

```
Read {SKILL_DIR}/skills/tracking-list/SKILL.md
```

This specification defines:
- 4 tracking types (Product / Model / Benchmark / Funding) with include/exclude criteria
- Source priority rankings
- Scoring criteria (1-10 scale with 5 dimensions)
- Timeliness validation rules (event date ≠ page date)
- Cross-verification requirements (7+ scores need 2+ independent sources)
- Record format for the report

**Internalize the specification before writing the report.** Pay special attention to the scoring reference tables and type classification guide.

---

## Step 3: Generate Report

1. Read the JSON output from Step 1
2. Read the report template: `Read {SKILL_DIR}/templates/report.md`
3. Generate `report_{YYYY-MM-DD}.md` in the working directory

**Report generation rules:**
- Filter out any excluded types (if `--exclude` was specified)
- Sort items by score within each type section
- **TLDR section**: Only items with score 7+ (across all types), sorted high to low
- **Type sections**: Group by score range (9-10 / 7-8 / 5-6 / 3-4)
- For items with score 7+, include multi-source verification if available
- Use the record format from the tracking specification
- Fill in the statistics summary table

**Item format in report:**

For high-score items (7+):
```markdown
### {Entity} - {Event description}

| Field | Value |
|-------|-------|
| **Type** | Product / Model / Benchmark / Funding |
| **Score** | X.X |
| **Published** | YYYY-MM-DD HH:MM UTC+8 |
| **Source** | [Source Name](URL) |

**Summary:**
- Key point 1
- Key point 2
- Key point 3
```

For lower-score items (3-6), use compact table format.

---

## Step 4: Generate Infographics (Optional)

**This step is optional. Skip if no image generation capability is available or configured.**

1. Read the infographic specification:
   ```
   Read {SKILL_DIR}/skills/gen-infographic/SKILL.md
   ```

2. **Cover image**: Sort by score and select the **top 4-5** updates (across all types). Build prompt using the Cover Prompt Template.

3. **Per-type images**: For each type (Model/Product/Benchmark/Funding), check if it has 7+ score items. If yes, build a prompt using the Per-Type Prompt Template.
   - Default (`IMAGE_GEN_TYPES=auto`): only types with 7+ score items
   - Set `IMAGE_GEN_TYPES=all` for all types, `none` for cover only

4. Generate 16:9 landscape images using one of:

   **Option A** — Native tool (Claude Code or other tools with built-in image generation):
   Use your tool's built-in image generation capability (e.g. `gen_images`), one call per image.

   **Option B** — Python script batch mode (any environment, requires `IMAGE_GEN_PROVIDER` configured):
   Build a manifest JSON with all prompts and outputs, then run:
   ```bash
   cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/manifest.json
   ```
   Supported providers: `gemini`, `gpt`, `minimax`. See [Configuration](#configuration) for API keys.

   Add `--stitch` to also produce a single combined long image (`news_infographic_YYYY-MM-DD_combined.png`) for social sharing. Requires `pip install Pillow`.

   **Long image mode**: To generate a cohesive vertical long image instead of separate standalone images, follow the **Long Image Strategy** section in `skills/gen-infographic/SKILL.md`. The strategy adapts based on content volume: sparse content (≤ 8 items) produces a single combined 9:16 portrait image; richer content produces a cover (16:9) + per-type sections (9:16) stitched together. Manifest items support an optional `"aspect_ratio"` field (e.g. `"9:16"`).

5. Insert images into the report:
   - Cover image at the beginning
   - Per-type images at the top of each type section

---

## Entity Reference

The `entities/` directory contains detailed entity registries organized by tracking group:

| File | Scope | Entities |
|------|-------|----------|
| `entities/ai-labs.md` | Frontier AI Labs + China AI | OpenAI, Anthropic, Google, Meta AI, xAI, Microsoft, Qwen, DeepSeek, + 11 more |
| `entities/model-infra.md` | Model Infrastructure | NVIDIA, Mistral, Cohere, Perplexity, AWS, Together, Groq, Apple |
| `entities/coding-agent.md` | Coding Agent | Cursor, Cline, OpenCode, Droid, OpenClaw, Windsurf, + 5 more |
| `entities/ai-apps.md` | AI Applications | v0, bolt.new, Lovable, Replit, Lovart, Manus, + 2 more |
| `entities/vision-media.md` | Vision & Media | Midjourney, Runway, Pika, FLUX, ElevenLabs, + 7 more |
| `entities/benchmarks-academic.md` | Benchmarks & Academic | LMSYS, HuggingFace, arXiv channels, industry media |
| `entities/kol.md` | Key Opinion Leaders | Andrej Karpathy, AK, Andrew Ng, Swyx, Simon Willison, + 3 more |
| `entities/trending-discovery.md` | Trending Discovery | GitHub Trending, Product Hunt, Hacker News, Reddit |

Each file lists X/Twitter accounts, key people, official blogs, changelogs, GitHub repos, and other source URLs for every tracked entity. Read these files when you need to verify or supplement the automated collection.

### Custom Entities

Users can add their own tracked entities by placing markdown files in `entities/custom/` (or `~/.config/morning-ai/entities/`, or a path set via `CUSTOM_ENTITIES_DIR`). Custom entity files use a simplified format — see `entities/custom-example.md` for the template. Custom entities are automatically merged into the built-in registries at runtime and collected alongside the default 80+ entities.

---

## Scheduling

Morning-AI is designed for daily automated execution. Each run produces date-stamped files (`report_YYYY-MM-DD.md`, `data_YYYY-MM-DD.json`), making it safe to run on a recurring schedule.

### Schedule Configuration

Use `--schedule` to set a custom cron expression (default: `0 8 * * *`):

| Parameter | Format | Default | Example |
|-----------|--------|---------|---------|
| `--schedule` | Cron expression (5-field) | `0 8 * * *` (daily 8am) | `0 9 * * 1-5` (weekdays 9am) |

The schedule is passed to the agent's native scheduler (CronCreate, /loop, system cron, etc.). Morning-AI itself does not run a scheduler — it relies on the host agent or system to trigger runs.

### Unattended Behavior

- **Idempotent**: Re-running on the same date overwrites previous output — no duplicate accumulation
- **No interactive prompts**: All steps run without user input when API keys are configured
- **Partial success**: If some sources fail, the report generates with available data and logs warnings
- **Timeout**: Allow 3 min (default depth) or 5 min (deep)

### Agent Integration Examples

**Claude Code** (CronCreate / loop):
```
/loop 24h /morning-ai
```

With custom schedule:
```
/morning-ai --schedule "0 9 * * 1-5"
```

**System cron** (manual setup):
```bash
0 8 * * * cd /path/to/workspace && claude -p "/morning-ai"
```

**OpenClaw / always-on bot**:
```yaml
schedule: "0 8 * * *"
skill: morning-ai
```

---

## Configuration

### Config File Locations (priority order)

1. **Environment variables** (highest priority)
2. **Project config**: `.env` in skill directory
3. **Global config**: `~/.config/morning-ai/.env`

### Config File Format

```bash
# ~/.config/morning-ai/.env
SCRAPECREATORS_API_KEY=your_key
GITHUB_TOKEN=ghp_xxx
YOUTUBE_API_KEY=your_key
DISCORD_TOKEN=your_token
BRAVE_API_KEY=your_key
EXA_API_KEY=your_key
```

### Free Sources (no API key needed)

| Source | API | Rate Limit |
|--------|-----|-----------|
| Reddit | Public JSON | Generous |
| Hacker News | Algolia API | Generous |
| HuggingFace | Public API | Generous |
| arXiv | Public API | Generous |

---

## Security & Permissions

- **Data access**: Reads public web/platform data only. No private or authenticated content is accessed.
- **API keys**: Stored locally in `.env` files. Never transmitted except to their respective APIs.
- **File writes**: Only writes report files (`report_*.md`, `data_*.json`) and cache files to the skill/working directory.
- **Network**: Outbound HTTP/HTTPS requests to public APIs (Twitter, Reddit, GitHub, etc.). No inbound connections.
- **No telemetry**: No usage data is collected or sent anywhere.
