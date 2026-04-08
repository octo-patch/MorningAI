# MorningAI

A multi-agent system that tracks 76+ AI entities, collects updates from 9 sources, and generates structured daily reports with cover infographics.

Built as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin.

## How It Works

```
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

8 sub-agents run concurrently, each checking its assigned entities across X/Twitter, GitHub, HuggingFace, arXiv, Reddit, HN, YouTube, Discord, and web search. Results are scored (1-10), deduplicated, cross-verified, and aggregated into a Markdown report.

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

All items are classified into 4 types: **Product** (feature launches, version releases), **Model** (new models, open-source weights), **Benchmark** (leaderboard changes, papers), **Funding** (rounds, acquisitions, milestones).

## Setup

```bash
git clone https://github.com/octo-patch/MorningAI.git
cd MorningAI
```

Create a `.env` file with API keys:

```env
SCRAPECREATORS_API_KEY=your_key    # X/Twitter (required)
GITHUB_TOKEN=ghp_xxx               # GitHub (optional)
YOUTUBE_API_KEY=your_key            # YouTube (optional)
DISCORD_TOKEN=your_token            # Discord (optional)
BRAVE_API_KEY=your_key              # Web search (optional)
```

Run inside Claude Code:

```bash
claude
```
```
Track today's AI updates and generate the daily report.
```

Or run the collector standalone:

```bash
python3 scripts/collect.py --date 2026-04-07 --output report.json
```

## License

MIT
