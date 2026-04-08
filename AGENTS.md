# MorningAI

Daily-scheduled AI news tracker. Collects updates from 76+ AI entities across 9 data sources every 24 hours. Generates scored, deduplicated Markdown reports with optional cover infographics.

## Skills

This repository provides a single skill: **morning-ai**.

To use it, read `SKILL.md` at the repository root — it contains full step-by-step instructions for data collection, report generation, and optional infographic creation.

Invoke with: `/morning-ai` or `morning-ai`

## Quick Reference

- **Entry point**: `SKILL.md` (step-by-step workflow)
- **Collector script**: `skills/tracking-list/scripts/collect.py`
- **Entity registries**: `entities/*.md` (80+ tracked entities)
- **Report template**: `templates/report.md`
- **Config**: `~/.config/morning-ai/.env` or project `.env`

## Configuration

Required API keys should be configured in `~/.config/morning-ai/.env`:

```
SCRAPECREATORS_API_KEY=...   # X/Twitter data (required for X source)
```

Optional keys unlock more sources: `GITHUB_TOKEN`, `YOUTUBE_API_KEY`, `DISCORD_TOKEN`, `BRAVE_API_KEY`, `EXA_API_KEY`.

Without any API keys, 4 free sources work out of the box: Reddit, Hacker News, HuggingFace, arXiv.

## Scheduling

Default schedule: daily at 08:00 UTC+8. Each run produces date-stamped files (`report_YYYY-MM-DD.md`, `data_YYYY-MM-DD.json`), making it safe to run unattended on a recurring schedule.

## Permissions

- Reads public web/API data only
- Writes report and data files to the working directory
- Outbound HTTPS requests to public APIs (X, Reddit, GitHub, HuggingFace, arXiv, etc.)
- No telemetry, no inbound connections
