# MorningAI

A multi-agent system that automatically tracks 76+ AI entities across the industry, collects updates from 9 data sources, and generates structured daily reports with cover infographics.

Built as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin -- run it inside Claude Code and it orchestrates everything with concurrent sub-agents.

## How It Works

```
              config.yaml (system prompt)
                       |
                 Coordinator Agent
                /    |    |    \
        frontier  model  china  coding  ai-apps  vision  benchmarks  trending
          labs    infra    ai    tools            media   academic    discovery
            \      |      |      /        |        |        |          /
             -------------------------------------------------------
                        |                                  |
                  collect.py (9 sources)          /tracking-list skill
                        |                                  |
                  score + dedupe                    /gen-infographic skill
                        |                                  |
                  report_{date}.md            news_infographic_{date}.png
```

**Coordinator Agent** dispatches 8 sub-agents concurrently. Each sub-agent checks its assigned entities across X/Twitter, GitHub, HuggingFace, arXiv, Reddit, Hacker News, YouTube, Discord, and web search. Results are scored (1-10), deduplicated, cross-verified, and aggregated into a daily Markdown report with a cover infographic.

## Tracked Entities (76+)

| Agent | Entities | Count |
|-------|----------|-------|
| **frontier-labs** | OpenAI, Anthropic, Google DeepMind, Meta AI, xAI, Microsoft | 6 |
| **model-infra** | NVIDIA, Mistral AI, Cohere, Perplexity AI, AWS, Together AI, Groq, Apple/MLX | 8 |
| **china-ai** | Qwen, DeepSeek, Doubao, GLM/Zhipu, Kimi, MiniMax, Kling, InternLM, LongCat, 01.AI, Baichuan, StepFun, Tencent Hunyuan | 13 |
| **coding-tools** | Cursor, Cline, OpenCode, Droid, OpenClaw, Windsurf, Augment Code, Aider, Devin, browser-use | 10 |
| **ai-apps** | v0, bolt.new, Lovable, Replit, Lovart, Manus, Genspark, Character.ai | 8 |
| **vision-media** | Midjourney, Runway, Pika, Luma AI, FLUX, Ideogram, Adobe Firefly, Leonardo AI, Lightricks, Stability AI, ElevenLabs, Udio/Suno | 12 |
| **benchmarks-academic** | LMSYS, LMArena, Artificial Analysis, HuggingFace, Scale AI, KOLs, arXiv channels, industry media | 20+ |
| **trending-discovery** | GitHub Trending, Product Hunt, Hacker News, Reddit | 4 sources |

## Content Types

Every tracked item is classified into one of 4 types:

| Type | What's tracked |
|------|----------------|
| **Product** | Feature launches, version releases, API/SDK updates, pricing changes |
| **Model** | New model releases, open-source weights, capability upgrades |
| **Benchmark** | Leaderboard changes, academic papers, technical reports |
| **Funding** | Series B+ rounds, acquisitions, major partnerships, milestones |

## Data Sources

| Source | Method | Auth Required |
|--------|--------|---------------|
| X/Twitter | ScrapeCreators API | Yes |
| GitHub | Releases API | Optional |
| HuggingFace | Public API | No |
| arXiv | Public API | No |
| Reddit | Public JSON | No |
| Hacker News | Algolia API | No |
| YouTube | Data API | Yes |
| Discord | Bot API | Yes |
| Web Search | Brave / Exa | Yes |

## Project Structure

```
MorningAI/
├── config.yaml                  # System prompt for the coordinator agent
├── agents/                      # 8 sub-agent definitions
│   ├── frontier-labs.md
│   ├── model-infra.md
│   ├── china-ai.md
│   ├── coding-tools.md
│   ├── ai-apps.md
│   ├── vision-media.md
│   ├── benchmarks-academic.md
│   └── trending-discovery.md
├── scripts/
│   ├── collect.py               # Data collection orchestrator
│   └── lib/                     # Collectors, scoring, dedup (17 modules)
│       ├── entities.py          # Registry of 76+ entities and their sources
│       ├── schema.py            # TrackerItem / DailyReport data models
│       ├── score.py             # 1-10 importance scoring
│       ├── dedupe.py            # Source dedup + cross-source linking
│       ├── x_twitter.py         # X/Twitter collector
│       ├── github.py            # GitHub releases collector
│       ├── huggingface.py       # HuggingFace model collector
│       ├── arxiv.py             # arXiv paper collector
│       ├── reddit.py            # Reddit collector
│       ├── hackernews.py        # Hacker News collector
│       ├── youtube.py           # YouTube collector
│       ├── discord.py           # Discord collector
│       ├── websearch.py         # Brave/Exa web search collector
│       └── ...
├── skills/
│   ├── tracking-list/SKILL.md   # Unified tracking specification
│   └── gen-infographic/SKILL.md # Infographic generation rules
├── templates/                   # Markdown templates for plans/drafts/reports
└── .claude-plugin/plugin.json   # Claude Code plugin manifest
```

## Setup

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Clone and configure

```bash
git clone https://github.com/octo-patch/MorningAI.git
cd MorningAI
```

Create a `.env` file with your API keys:

```env
# Required for X/Twitter collection
SCRAPECREATORS_API_KEY=your_key

# Optional - enhances collection coverage
GITHUB_TOKEN=ghp_xxx
YOUTUBE_API_KEY=your_key
DISCORD_TOKEN=your_token
BRAVE_API_KEY=your_key
EXA_API_KEY=your_key
```

### 3. Run

Launch Claude Code in the project directory:

```bash
claude
```

Then ask it to generate a daily report:

```
Track today's AI updates and generate the daily report.
```

The coordinator agent will:
1. Dispatch 8 sub-agents concurrently
2. Collect updates from all configured sources
3. Score, deduplicate, and cross-verify items
4. Generate `report_{date}.md` and `news_infographic_{date}.png`

### Standalone Data Collection

The Python collector can run independently:

```bash
python3 scripts/collect.py --date 2026-04-07 --depth default --output report.json
```

Options:
- `--date YYYY-MM-DD` - Target date (default: today)
- `--depth quick|default|deep` - Collection depth
- `--sources x reddit github ...` - Specific sources only
- `--output PATH` - Output file (default: stdout)
- `--cache-ttl HOURS` - Cache TTL (default: 12)

## Scoring System

Items are scored 1-10 across 5 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Impact | 30% | Industry-wide influence |
| Differentiation | 25% | First-of-kind or unique |
| Breakthrough | 20% | Technical/strategic leap |
| Coverage | 15% | Number of users affected |
| Timeliness | 10% | Time-sensitivity of the info |

| Score | Level | Example |
|-------|-------|---------|
| 9-10 | Major Event | Flagship model launch, $1B+ funding |
| 7-8 | Important | New model version, major feature upgrade |
| 5-6 | Routine | Minor version update, regular feature |
| 3-4 | Minor | API param tweak, doc update |
| 1-2 | Trivial | Typo fix, dependency bump |

Items scoring 7+ require multi-source verification.

## License

MIT
