# MorningAI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://python.org)
[![Entities](https://img.shields.io/badge/Tracked_Entities-80%2B-orange.svg)](#tracked-entities-80)
[![Sources](https://img.shields.io/badge/Data_Sources-9-green.svg)](#how-it-works)
[![Platforms](https://img.shields.io/badge/Platforms-6%2B-purple.svg)](#install)

**What happened in AI today?** — An AI news tracking skill that runs inside your coding agent. No Docker, no servers — just invoke `/morning-ai` in Claude Code, Codex, Cursor, Gemini CLI, or any SKILL.md-compatible tool. Monitors 80+ entities across 9 data sources, generates scored daily reports with optional infographics.

## Features

- **Skill-Native** — Runs inside your AI coding tool (Claude Code, Codex, Cursor, Gemini CLI). No Docker, no servers, no extra infra — just `/morning-ai`
- **Entity-Centric Tracking** — 80+ curated entities across AI labs, model infra, coding agents, apps, vision/media, benchmarks, KOLs. Per-entity cross-platform handles (X, GitHub, HF, arXiv, YouTube, Discord), not keyword search
- **9 Concurrent Sources** — X/Twitter, Reddit, HN, GitHub, HuggingFace, arXiv, web search, YouTube, Discord. 4 sources free without API keys
- **Smart Scoring** — 5-dimension weighted scoring: Impact (30%), Differentiation (25%), Breakthrough (20%), Coverage (15%), Timeliness (10%). Score 7+ items auto-verified across multiple independent sources
- **Custom Watchlists** — Add your own entities via simple markdown files — no code changes needed
- **5 Infographic Styles** — `classic`, `dark`, `glassmorphism`, `newspaper`, `tech` — ready for social sharing
- **Scheduled & Unattended** — Idempotent daily runs, no interactive prompts, partial success support

## Sample Output

Here's what a MorningAI daily report looks like — 26 updates scored, deduplicated, and verified across 9 sources in under 50 seconds:

<details>
<summary><b>TLDR — Today's 7+ Score Updates (click to expand)</b></summary>

- **[Model] Anthropic - Claude 4.5 Sonnet released** (9.2): New mid-tier model with +18% SWE-Bench, 200K context, 40% faster output
- **[Model] Google DeepMind - Gemini 2.5 Flash public preview** (8.8): 1M context, native multimodal, free tier on AI Studio
- **[Product] Cursor - Background Agents GA** (8.5): Autonomous agents, cloud sandbox, multi-file refactoring
- **[Model] DeepSeek - V3-0407 open-weight release** (8.3): 671B MoE, MIT license, weights on HuggingFace
- **[Product] OpenAI - Codex CLI open-sourced** (8.0): Terminal agent, suggest/auto-edit/full-auto modes
- **[Benchmark] LMSYS - Chatbot Arena April rankings** (7.5): Claude 4.5 Sonnet #2 overall, Gemini 2.5 Pro #1 coding
- **[Product] GitHub - Copilot Coding Agent preview** (7.3): Autonomous agent on issues, creates PRs in sandbox
- **[Funding] Windsurf - $200M Series C at $3B** (7.1): Largest round in coding tools space

</details>

> Full sample report: [samples/report_2026-04-08.md](samples/report_2026-04-08.md)
> Raw data JSON: [samples/data_2026-04-08.json](samples/data_2026-04-08.json)
> Infographic style previews: [docs/styles.md](docs/styles.md)

## How It Works

```
SKILL.md (loaded by any AI tool)
    |
    +- Step 1: python3 skills/tracking-list/scripts/collect.py  ->  data_{date}.json
    |           (9 sources, concurrent, score + dedupe)
    |
    +- Step 2: Read skills/tracking-list/SKILL.md  ->  scoring & format spec
    |
    +- Step 3: Write report_{date}.md  ->  structured daily report
    |
    +- Step 4: (optional) Read skills/gen-infographic/SKILL.md  ->  cover image
```

The Python collector runs 9 sources concurrently (X/Twitter, Reddit, HN, GitHub, HuggingFace, arXiv, web search, YouTube, Discord), then scores, deduplicates, and cross-links results. The AI tool reads the JSON output and generates a formatted Markdown report.

## Install

### Claude Code

```bash
# Step 1: Add marketplace source
marketplace add octo-patch/MorningAI

# Step 2: Install the plugin
/plugin install morning-ai

# Step 3: Restart Claude Code, then use
/morning-ai
```

Or manual install:

```bash
git clone https://github.com/octo-patch/MorningAI.git ~/.claude/skills/morning-ai
```

### ClawHub

```bash
clawhub install morning-ai
```

### Gemini CLI

```bash
gemini extensions install https://github.com/octo-patch/MorningAI.git
```

### OpenAI Codex

If cloned or forked, Codex auto-discovers the plugin via `.codex-plugin/plugin.json` and `AGENTS.md` — no manual setup needed.

Or install as a skill:

```bash
git clone https://github.com/octo-patch/MorningAI.git ~/.agents/skills/morning-ai
```

### Other Tools (Cursor, Amp, Jules, etc.)

`AGENTS.md` at the repo root is an open standard recognized by Codex, Cursor, Amp, Jules, and more. Clone the repo and the tool will auto-discover it.

### Manual (any tool)

```bash
git clone https://github.com/octo-patch/MorningAI.git
cd MorningAI
```

## Setup

Create a config file at `~/.config/morning-ai/.env`:

```env
SCRAPECREATORS_API_KEY=your_key    # X/Twitter (required for X source)
GITHUB_TOKEN=ghp_xxx               # GitHub (optional)
YOUTUBE_API_KEY=your_key            # YouTube (optional)
DISCORD_TOKEN=your_token            # Discord (optional)
BRAVE_API_KEY=your_key              # Web search (optional)
```

Without any API keys, 4 free sources work out of the box: **Reddit**, **Hacker News**, **HuggingFace**, **arXiv**.

## Custom Entity Watchlist

Track your own entities beyond the built-in 80+ by creating a markdown file:

```bash
cp entities/custom-example.md entities/custom/my-watchlist.md
```

Edit the file with your entities:

```markdown
## My Startup

| Platform | Value |
|----------|-------|
| X | @my_startup, @founder |
| GitHub | my-startup-org |
| HuggingFace | my-startup |
| Reddit | MyStartup |
```

Each entity starts with a `## Name` heading followed by a `| Platform | Value |` table. Not all platforms are required — add only what you need. Supported platforms: `X`, `GitHub`, `HuggingFace`, `arXiv`, `Web`, `Reddit`, `HN`, `YouTube`, `Discord`.

Custom entity files are loaded from (in priority order):

1. `CUSTOM_ENTITIES_DIR` env var
2. `~/.config/morning-ai/entities/`
3. `entities/custom/` in the project directory

Files in `entities/custom/` are gitignored, so your watchlists stay local.

## Usage

Invoke the skill in your AI tool:

```
/morning-ai
```

Or run the collector standalone:

```bash
python3 skills/tracking-list/scripts/collect.py --date 2026-04-08 --output report.json
```

## Infographic Styles

Set `IMAGE_STYLE` in your `.env` to choose a visual style for generated infographics:

| Style | Description |
|-------|-------------|
| `classic` | Clean editorial magazine — off-white background, navy/coral/teal accents **(default)** |
| `dark` | Dark mode — charcoal background, electric blue/violet accents |
| `glassmorphism` | Frosted glass cards on soft gradient background — modern SaaS feel |
| `newspaper` | Classic newsprint — serif typography, cream/black/crimson, broadsheet layout |
| `tech` | Terminal aesthetic — dark background, monospace, cyan/green/amber accents |

```env
IMAGE_STYLE=dark
IMAGE_GEN_PROVIDER=gemini
```

## Tracked Entities (80+)

| Group | Entities | Count |
|-------|----------|-------|
| **ai-labs** | OpenAI, Anthropic, Google, Meta AI, xAI, Microsoft, Qwen, DeepSeek, Doubao, GLM, Kimi, MiniMax, Kling, InternLM, LongCat, Yi, Baichuan, StepFun, Hunyuan | 19 |
| **model-infra** | NVIDIA, Mistral AI, Cohere, Perplexity AI, AWS, Together AI, Groq, Apple/MLX, vLLM, SGLang, KTransformers | 11 |
| **coding-agent** | Cursor, Cline, OpenCode, Droid, OpenClaw, Windsurf, Augment, Aider, Devin, browser-use, Hermes Agent | 11 |
| **ai-apps** | v0, bolt.new, Lovable, Replit, Lovart, Manus, Genspark, Character.ai | 8 |
| **vision-media** | Midjourney, FLUX, Ideogram, Adobe Firefly, Leonardo AI, Stability AI, Lightricks, Runway, Pika, Luma AI, ElevenLabs, Udio/Suno | 12 |
| **benchmarks-academic** | LMSYS, LMArena, Artificial Analysis, HuggingFace, Scale AI SEAL, OpenCompass, LiveBench, WildBench, Terminal-Bench, Vals AI, Design Arena, Vending-Bench, SimpleBench, Repo Bench, Replicate, 5 paper channels, 2 Reddit communities, 4 industry media | 20+ |
| **kol** | Andrej Karpathy, AK, Andrew Ng, Rowan Cheung, Ben Tossell, Elie Bakouch, Swyx, Simon Willison | 8 |
| **trending-discovery** | GitHub Trending, Product Hunt, Hacker News, Reddit | 4 sources |

All items are classified into 4 types: **Product**, **Model**, **Benchmark**, **Funding**.

## Deploy to Multiple Tools

```bash
bash scripts/sync.sh
```

Distributes the skill to `~/.claude/skills/`, `~/.agents/skills/`, and `~/.codex/skills/`.

## License

MIT
