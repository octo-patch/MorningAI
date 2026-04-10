---
name: morning-ai
version: "1.1.1"
description: "Daily-scheduled AI news tracker. Collects updates from 80+ AI entities across 9 sources every 24 hours (default 08:00 UTC+8). Generates scored, deduplicated Markdown reports. Supports unattended cron/scheduled execution with date-stamped idempotent output."
argument-hint: 'morning-ai, morning-ai --exclude Funding, morning-ai --depth deep, morning-ai --lang zh, morning-ai --schedule "0 9 * * *"'
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

## Step 0: Configuration Gate (REQUIRED — must complete before any other step)

**Run this command FIRST before doing anything else:**

```bash
if [ -f "$HOME/.config/morning-ai/.env" ] || [ -f ".claude/morning-ai.env" ] || [ -f ".env" ]; then echo "CONFIG_STATUS=READY"; else echo "CONFIG_STATUS=MISSING"; fi
```

**Branch on the output:**

- **If output is `CONFIG_STATUS=READY`** — read the config file, report which sources are active (N/9), then proceed to Step 1.
- **If output is `CONFIG_STATUS=MISSING`** — **STOP. You MUST complete the First-Time Onboarding below before proceeding to Step 1.**

### First-Time Onboarding (when `MISSING`)

> **CRITICAL: STOP HERE.**
> You MUST complete all onboarding steps below interactively with the user.
> Do NOT run Step 1 (data collection) until a config file exists and the gate check returns `READY`.
> Running data collection without configuration will produce incomplete results.

Walk the user through setup interactively, waiting for their response at each step:

1. **Welcome** — briefly explain what morning-ai does: tracks 80+ AI entities across 9 sources, generates scored daily reports
2. **Show what works for free** — 4 sources need no API keys:
   - Reddit (public JSON), Hacker News (Algolia API), HuggingFace (public API), arXiv (public API)
3. **Ask the user** which additional sources they want to enable, and present the keys needed:

| Key | Source | Get it at |
|-----|--------|-----------|
| `SCRAPECREATORS_API_KEY` | X/Twitter search | https://scrapecreators.com |
| `GITHUB_TOKEN` | GitHub releases & repos | https://github.com/settings/tokens |
| `YOUTUBE_API_KEY` | YouTube channels | https://console.cloud.google.com |
| `DISCORD_TOKEN` | Discord announcements | https://discord.com/developers |
| `BRAVE_API_KEY` | Brave web search | https://brave.com/search/api |
| `EXA_API_KEY` | Exa web search | https://exa.ai |

4. **Ask about infographics** (optional):

| Key | Description |
|-----|-------------|
| `IMAGE_GEN_PROVIDER` | Provider: `gemini` \| `gpt` \| `minimax` \| `none` (default: none) |
| `IMAGE_STYLE` | Style: `classic` \| `dark` \| `glassmorphism` \| `newspaper` \| `tech` |
| `GEMINI_API_KEY` | Google Gemini/Imagen (https://aistudio.google.com/apikey) |
| `OPENAI_API_KEY` | OpenAI gpt-image-1 (https://platform.openai.com/api-keys) |
| `MINIMAX_API_KEY` | MiniMax global(https://www.minimax.io) |
| `MINIMAX_API_KEY` | MiniMax cn (https://platform.minimaxi.com) |

5. **Create the config file** — collect the keys the user provides and write them to `~/.config/morning-ai/.env` in `KEY=value` format (one per line). Create the directory if needed: `mkdir -p ~/.config/morning-ai`
6. **Confirm** — show how many sources are now active (N/9)
7. **Verify** — re-run the gate check to confirm `CONFIG_STATUS=READY`:
   ```bash
   if [ -f "$HOME/.config/morning-ai/.env" ] || [ -f ".claude/morning-ai.env" ] || [ -f ".env" ]; then echo "CONFIG_STATUS=READY"; else echo "CONFIG_STATUS=MISSING"; fi
   ```
   Only proceed to Step 1 if the output is `READY`.
8. If the user wants to skip API key setup and use only free sources, create a minimal config file first, then proceed to Step 1:
   ```bash
   mkdir -p ~/.config/morning-ai && echo "# morning-ai config — free sources only" > ~/.config/morning-ai/.env
   ```

---

## Language

| Parameter | Default | Example |
|-----------|---------|---------|
| `--lang` | `en` (English) | `--lang zh` (Chinese), `--lang ja` (Japanese) |

**Rules:**
- **Default is English.** All report text — titles, summaries, section headers, table labels, and bullet points — must be written in English unless `--lang` is specified.
- If `--lang` is specified, use that language for all human-readable content instead.
- **Entity names are proper nouns** (OpenAI, DeepSeek, Midjourney, etc.) — keep them as-is regardless of language.
- When source data is in a different language than the target, **translate it** into the target language during report generation.
- The `--lang` setting also applies to infographic prompt content (see Step 4).

---

> **Prerequisite:** Step 0 must have returned `CONFIG_STATUS=READY`. If you have not completed Step 0, go back and run it now.

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
- **Language**: Write all content in the target language (default: English). If source data is in a different language, translate it. Entity names (proper nouns) stay as-is.
- **Source links**: Every item in the report MUST include a clickable source link `[Source Name](URL)` pointing to the original content. This applies to all sections: TLDR items, high-score detailed entries, and compact table rows. Readers must be able to click through to the original source for every item.
- Filter out any excluded types (if `--exclude` was specified)
- Sort items by score within each type section
- **TLDR section**: Only items with score 7+ (across all types), sorted high to low. Each item must include a source link `[[Source](URL)]` at the end.
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

For lower-score items (3-6), use compact table format. The Source column must contain clickable `[Name](URL)` links.

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
