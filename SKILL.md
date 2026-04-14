---
name: morning-ai
version: "1.1.8"
description: "Daily-scheduled AI news tracker. Collects updates from 80+ AI entities across 5 automated sources + agent X/Twitter search every 24 hours (default 08:00 UTC+8). Generates scored, deduplicated Markdown reports. Supports unattended cron/scheduled execution with date-stamped idempotent output."
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
      optionalEnv:
        - GITHUB_TOKEN
      bins:
        - python3
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

> **Permissions overview:** Collects public data from Reddit, Hacker News, GitHub, HuggingFace, and arXiv. X/Twitter updates are discovered via agent web search. Requires optional API keys configured in `.env` or `~/.config/morning-ai/.env`. Writes report files to the current working directory. See [Configuration](#configuration) for details.

Track 76+ AI entities across 5 automated data sources + agent-driven X/Twitter search. Collect updates from the past 24 hours, score and deduplicate them, and generate a structured Markdown daily report. Covers 4 types: **Product** (feature launches, version releases), **Model** (new models, open-source weights), **Benchmark** (leaderboard changes, papers), **Funding** (rounds, acquisitions, milestones).

---

## Step 0: Configuration Gate (REQUIRED — must complete before any other step)

**Run this command FIRST before doing anything else:**

```bash
if [ -f "$HOME/.config/morning-ai/.env" ] || [ -f ".claude/morning-ai.env" ] || [ -f ".env" ]; then echo "CONFIG_STATUS=READY"; else echo "CONFIG_STATUS=MISSING"; fi
```

**Branch on the output:**

- **If output is `CONFIG_STATUS=READY`** — read the config file, report which sources are active, then proceed to Step 1.
- **If output is `CONFIG_STATUS=MISSING`** — **STOP. You MUST complete the First-Time Onboarding below before proceeding to Step 1.**

### First-Time Onboarding (when `MISSING`)

> **CRITICAL: STOP HERE.**
> You MUST complete all onboarding steps below interactively with the user.
> Do NOT run Step 1 (data collection) until a config file exists and the gate check returns `READY`.
> Running data collection without configuration will produce incomplete results.

Walk the user through setup interactively, waiting for their response at each step:

1. **Welcome** — briefly explain what morning-ai does: tracks 80+ AI entities across 5 automated sources + agent X/Twitter search, generates scored daily reports
2. **Show what works for free** — 5 automated sources (4 need no API keys, 1 optional):
   - Reddit (public JSON), Hacker News (Algolia API), HuggingFace (public API), arXiv (public API)
   - GitHub (public API, optional `GITHUB_TOKEN` for higher rate limits)
   - X/Twitter updates are discovered via agent web search (no API key needed)
3. **Ask the user** if they want to enable GitHub with higher rate limits:

| Key | Source | Get it at |
|-----|--------|-----------|
| `GITHUB_TOKEN` | GitHub releases & repos (higher rate limit) | https://github.com/settings/tokens |

4. **Ask about infographics** (optional):

| Key | Description |
|-----|-------------|
| `IMAGE_GEN_PROVIDER` | Provider: `gemini` \| `minimax` \| `none` (default: none) |
| `IMAGE_STYLE` | Style: `classic` \| `dark` \| `glassmorphism` \| `newspaper` \| `tech` |
| `GEMINI_API_KEY` | Google Gemini/Imagen (https://aistudio.google.com/apikey) |
| `MINIMAX_API_KEY` | MiniMax global(https://www.minimax.io) |
| `MINIMAX_API_KEY` | MiniMax cn (https://platform.minimaxi.com) |

5. **Ask about social content distribution** (optional):
   - Enable social content generation? Set `SOCIAL_ENABLED=true`
   - Which platforms? X (Twitter), Xiaohongshu (Little Red Book), or both
   - For advanced multi-account/multi-style setup, create `~/.config/morning-ai/social_channels.json` (see `skills/gen-social/SKILL.md` for schema). For quick single-channel setup, just set `SOCIAL_PLATFORM`, `SOCIAL_STYLE`, and `SOCIAL_LANG` env vars.

6. **Create the config file** — collect the keys the user provides and write them to `~/.config/morning-ai/.env` in `KEY=value` format (one per line). Create the directory if needed: `mkdir -p ~/.config/morning-ai`
7. **Confirm** — show how many sources are now active (N/9)
8. **Verify** — re-run the gate check to confirm `CONFIG_STATUS=READY`:
   ```bash
   if [ -f "$HOME/.config/morning-ai/.env" ] || [ -f ".claude/morning-ai.env" ] || [ -f ".env" ]; then echo "CONFIG_STATUS=READY"; else echo "CONFIG_STATUS=MISSING"; fi
   ```
   Only proceed to Step 1 if the output is `READY`.
9. If the user wants to skip API key setup and use only free sources, create a minimal config file first, then proceed to Step 1:
   ```bash
   mkdir -p ~/.config/morning-ai && echo "# morning-ai config — free sources only" > ~/.config/morning-ai/.env
   ```

---

## Language

| Parameter | Default | Example |
|-----------|---------|---------|
| `--lang` | `en` (English) | `--lang zh` (Chinese), `--lang ja` (Japanese) |

**Rules:**
- **Default is English. Unless `--lang` is explicitly specified, the report MUST be written entirely in English.** All report text — titles, summaries, section headers, table labels, bullet points, "Why It Matters" analysis, and all other human-readable content — must be in English.
- If `--lang` is specified, use that language for all human-readable content instead.
- **Entity names are proper nouns** (OpenAI, DeepSeek, Midjourney, etc.) — keep them as-is regardless of language.
- When source data is in a different language than the target (e.g. Chinese source → English report), **translate it** into the target language during report generation. Do NOT leave untranslated fragments.
- The `--lang` setting also applies to infographic prompt content (see Step 4).

---

> **Prerequisite:** Step 0 must have returned `CONFIG_STATUS=READY`. If you have not completed Step 0, go back and run it now.

## Step 1: Data Collection

Run the Python collector to gather data from automated sources:

```bash
cd {SKILL_DIR} && python3 skills/tracking-list/scripts/collect.py --date {YYYY-MM-DD} --depth default -o {CWD}/data_{YYYY-MM-DD}.json
```

**Parameters:**
- `--date`: Target date, default today (YYYY-MM-DD)
- `--depth`: Collection depth — `quick` (fast, fewer results), `default`, or `deep` (comprehensive)
- `--sources`: Specific sources only, e.g. `--sources reddit hackernews github`
- `-o`: Output JSON file path

**What it does:**
- Runs 5 collectors concurrently (Reddit, HN, GitHub, HuggingFace, arXiv)
- Time window: `[Yesterday 08:00, Today 08:00) UTC+8`
- Pipeline: collect → score (1-10) → deduplicate → cross-source link → verification bonus
- Returns structured JSON with all items, stats, and collection metadata

**Timeout:** Allow up to 3 minutes for default depth, 5 minutes for deep.

If the user provides `--exclude` types (e.g. `--exclude Funding`), note which types to filter out in Step 3.

### X/Twitter Search (Agent-driven)

After the automated collection completes, use **web search** to discover recent X/Twitter updates from tracked entities. The tracked X handles are listed in `{SKILL_DIR}/lib/entities.py` under `X_HANDLES`.

1. Search for recent AI news on X/Twitter using web search — focus on high-priority entities (major AI labs, trending products, key people)
2. For each discovered update, verify timeliness (must be within the 24-hour collection window)
3. Incorporate verified X/Twitter findings into the report in Step 3, attributing the source as X/Twitter with a link to the original post

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
- **Language**: Default is **English**. Write ALL content in English unless `--lang` is explicitly specified. If source data is in a different language, translate it. Entity names (proper nouns) stay as-is.
- **Source links**: Every item in the report MUST include a clickable source link `[Source Name](URL)` pointing to the original content. This applies to all sections: TLDR items, high-score detailed entries, and compact table rows. Readers must be able to click through to the original source for every item.
- **Detail quality**: Summary bullet points must include specific details — version numbers, percentage improvements, parameter counts, pricing, availability dates, benchmark scores. Avoid vague descriptions like "improved performance" or "major update" without concrete numbers or specifics.
- **Factual verification (CRITICAL)**: Every specific number (parameter count, benchmark score, pricing, context length, version number, funding amount) MUST be verified from an authoritative primary source (HuggingFace model card, official blog, changelog, benchmark site, etc.) before inclusion. **Never write a number from memory or inference** — if the detail cannot be confirmed from the collected source data, OMIT it rather than guess. An absent detail is always better than a wrong one. See `skills/tracking-list/SKILL.md` → "Factual Detail Verification" for the full protocol.
- Filter out any excluded types (if `--exclude` was specified)
- Sort items by score within each type section

### Report Detail Level Requirements

Write reports as **detailed and comprehensive as possible**. Each item should have enough bullet points to cover all important aspects of the news.

**Bullet point count by score:**

| Score | Min Bullet Points | Content Depth |
|-------|------------------|---------------|
| **9-10** | 5-8 points | Exhaustive coverage: what, why, how, technical specs, competitive context, availability, pricing, ecosystem impact |
| **7-8** | 4-6 points | Thorough coverage: what happened, key specs/numbers, why it matters, who's affected, timeline |
| **5-6** | 3-4 points | Solid coverage: what changed, key numbers, context |
| **3-4** | 1-2 points | Brief but specific: what changed, one key detail |

**Each bullet point must be substantive** — include at least one of:
- Specific numbers (benchmarks, parameters, pricing, performance gains)
- Named comparisons (vs. competitor X, vs. previous version Y)
- Concrete capabilities (what users can now do)
- Dates/timelines (when available, when rolling out)
- Technical details (architecture, training data, methods)

**"Why It Matters" section** (required for 7+ scores):
- Must be **analytical, not descriptive** — explain implications, not just restate facts
- Include competitive context (how this positions the company vs rivals)
- Include user/industry impact (what changes for practitioners, researchers, or end users)
- 2-4 sentences for 9-10 scores, 1-2 sentences for 7-8 scores

**"Key Data" table** (required for 7+ scores when quantitative data exists):
- Include benchmark scores with delta vs previous/competitor
- Include pricing with comparison
- Include model specs (parameters, context length, modalities)
- Include business metrics (funding amount, valuation, user count)

- **TLDR section**: Only items with score 7+ (across all types), sorted high to low. Each item includes a one-line summary with specifics, plus an _Impact_ sentence explaining why it matters. Must include a source link `[[Source](URL)]` at the end.
- **Type sections**: Group by score range (9-10 / 7-8 / 5-6 / 3-4)
- For items with score 7+, include multi-source verification if available
- Use the record format from the tracking specification
- Fill in the statistics summary table

**Item format in report:**

For top-score items (9-10):
```markdown
### {Entity} - {Event description}

| Field | Value |
|-------|-------|
| **Type** | Product / Model / Benchmark / Funding |
| **Score** | X.X |
| **Published** | YYYY-MM-DD HH:MM UTC+8 |
| **Source** | [Source Name](URL) |

**Summary:**
- Key point 1 (with specific numbers, versions, or metrics)
- Key point 2 (competitive comparison or positioning)
- Key point 3 (technical specs or architecture details)
- Key point 4 (availability, pricing, or rollout timeline)
- Key point 5 (ecosystem impact or integration details)
- (5-8 bullet points total — cover all important aspects exhaustively)

**Why It Matters:**
> 2-4 sentence analysis: industry impact, competitive significance, and what this changes for end users. Don't restate the summary — explain the implications and strategic context.

**Key Data** (required when quantitative metrics are available):
| Metric | Value |
|--------|-------|
| e.g. Benchmark | e.g. 92.3% (+5.1% vs previous) |
| e.g. Parameters | e.g. 671B total / 37B active |
| e.g. Pricing | e.g. $3/M input, $15/M output |
| e.g. Context | e.g. 1M tokens (+4x vs v3) |
```

For important items (7-8):
```markdown
### {Entity} - {Event description}

| Field | Value |
|-------|-------|
| **Type** | Product / Model / Benchmark / Funding |
| **Score** | X.X |
| **Published** | YYYY-MM-DD HH:MM UTC+8 |
| **Source** | [Source Name](URL) |

**Summary:**
- Key point 1 (with specific numbers, versions, or metrics)
- Key point 2 (what changed and why)
- Key point 3 (who's affected and how)
- Key point 4 (technical or business details)
- (4-6 bullet points total)

**Why It Matters:**
> 1-2 sentence analysis: industry impact, competitive significance, or what this changes for end users.

**Key Data** (include when quantitative metrics are available):
| Metric | Value |
|--------|-------|
| e.g. Benchmark | e.g. 92.3% (+5.1% vs previous) |
```

For mid-score items (5-6), use multi-line format with 3-4 concrete points:
```markdown
- **Entity** (X.X): Event description with specifics (version, capability, metric).
  - Detail 1: what changed, key numbers, comparison with previous version or competitors
  - Detail 2: additional context, availability, or technical specifics
  - Detail 3: implications or notable aspects
  Source: [Name](URL)
```

For lower-score items (3-4), use compact table format. The Source column must contain clickable `[Name](URL)` links.

---

## Step 4: Generate Infographics (Optional)

**This step is optional. Skip if no image generation capability is available or configured.**

1. Read the infographic specification:
   ```
   Read {SKILL_DIR}/skills/gen-infographic/SKILL.md
   ```

2. **Generate cover + per-type sections + stitch** (see **Image Strategy** in `skills/gen-infographic/SKILL.md`):
   - Always generate cover (16:9 landscape) + per-type section images (9:16 portrait), then stitch into one long image

3. **Cover image**: Sort by score and select the **top 4-5** updates (across all types). Build prompt using the Cover Prompt Template (16:9 landscape).

4. **Per-type section images**: For each type (Model/Product/Benchmark/Funding) with 7+ score items, build a prompt using the Per-Type Prompt Template (9:16 portrait).
   - Default (`IMAGE_GEN_TYPES=auto`): only types with 7+ score items
   - Set `IMAGE_GEN_TYPES=all` for all types, `none` for cover only

5. Generate images and stitch:

   **Option A** — Native tool (Claude Code or other tools with built-in image generation):
   Use your tool's built-in image generation capability, one call per image. Then stitch sections together.

   **Option B** — Python script batch mode (any environment, requires `IMAGE_GEN_PROVIDER` configured):
   Build a manifest JSON with all prompts and outputs, then run:
   ```bash
   cd {SKILL_DIR} && python3 skills/gen-infographic/scripts/gen_infographic.py --batch {CWD}/manifest.json --stitch
   ```
   Supported providers: `gemini`, `minimax`. See [Configuration](#configuration) for API keys. Requires `pip install Pillow`.

   The final output is **`news_infographic_YYYY-MM-DD_combined.png`** — a single long image containing cover + all section images.

6. Insert images into the report:
   - Combined long image at the beginning
   - Individual per-type images optionally at the top of each type section

---

## Step 5: Generate Social Content (Optional)

**Skip this step if `SOCIAL_ENABLED` is not `true` or no social channels are configured.**

Generate platform-optimized copy and images for social media distribution (X, Xiaohongshu, etc.).

1. Read the social content specification:
   ```
   Read {SKILL_DIR}/skills/gen-social/SKILL.md
   ```

2. Load channel configuration:
   - If `SOCIAL_CHANNELS_FILE` exists → read the JSON channel list
   - Else if `SOCIAL_PLATFORM` env var is set → build a single channel from `SOCIAL_PLATFORM` + `SOCIAL_STYLE` + `SOCIAL_LANG`
   - Else → skip this step

3. For each channel:
   a. Read the channel's template: `{SKILL_DIR}/skills/gen-social/templates/{platform}/{style}.md`
   b. Select top items from the report data (filter by `min_score`, limit by `items`, translate if `lang` differs from source)
   c. Generate copy following the template's format rules, tone, and character limits
   d. **Validate character counts** — each tweet ≤ 280 chars, Xiaohongshu title ≤ 20 chars, body ≤ 1000 chars
   e. Write copy to `{CWD}/social/social_{YYYY-MM-DD}_{channel_id}.md`
   f. If channel has `image: true` — generate platform-adapted images using the same providers as Step 4
      - X: 16:9 or 1:1 aspect ratio
      - Xiaohongshu: 3:4 portrait, carousel multi-image supported
   g. Write images to `{CWD}/social/social_{YYYY-MM-DD}_{channel_id}_{N}.png`

4. Write manifest to `{CWD}/social/social_{YYYY-MM-DD}_manifest.json` listing all generated files

**Channel config examples**: See `skills/gen-social/SKILL.md` for the full JSON schema and quick-setup env vars.

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
GITHUB_TOKEN=ghp_xxx
```

### Free Sources (no API key needed)

| Source | API | Rate Limit |
|--------|-----|-----------|
| Reddit | Public JSON | Generous |
| Hacker News | Algolia API | Generous |
| GitHub | Public API (optional token for higher limits) | 60 req/hr (unauthenticated) |
| HuggingFace | Public API | Generous |
| arXiv | Public API | Generous |
| X/Twitter | Agent web search | N/A |

---

## Security & Permissions

- **Data access**: Reads public web/platform data only. No private or authenticated content is accessed.
- **API keys**: Stored locally in `.env` files. Never transmitted except to their respective APIs.
- **File writes**: Only writes report files (`report_*.md`, `data_*.json`) and cache files to the skill/working directory.
- **Network**: Outbound HTTP/HTTPS requests to public APIs (Reddit, GitHub, etc.). No inbound connections.
- **No telemetry**: No usage data is collected or sent anywhere.
