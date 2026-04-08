# MorningAI

A universal AI news tracking skill that works across Claude Code, OpenCode, OpenClaw, Codex, and Gemini CLI. Tracks 80+ AI entities across 9 data sources and generates daily structured reports with optional cover infographics.

## How It Works

```
SKILL.md (loaded by any AI tool)
    │
    ├─ Step 1: python3 skills/tracking-list/scripts/collect.py  →  data_{date}.json
    │           (9 sources, concurrent, score + dedupe)
    │
    ├─ Step 2: Read skills/tracking-list/SKILL.md  →  scoring & format spec
    │
    ├─ Step 3: Write report_{date}.md  →  structured daily report
    │
    └─ Step 4: (optional) Read skills/gen-infographic/SKILL.md  →  cover image
```

The Python collector runs 9 sources concurrently (X/Twitter, Reddit, HN, GitHub, HuggingFace, arXiv, web search, YouTube, Discord), then scores, deduplicates, and cross-links results. The AI tool reads the JSON output and generates a formatted Markdown report.

## Install

### Claude Code

```bash
# Marketplace
marketplace add octo-patch/MorningAI

# Or manual install
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

```bash
git clone https://github.com/octo-patch/MorningAI.git ~/.agents/skills/morning-ai
```

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

## Usage

Invoke the skill in your AI tool:

```
/morning-ai
```

Or run the collector standalone:

```bash
python3 skills/tracking-list/scripts/collect.py --date 2026-04-08 --output report.json
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
