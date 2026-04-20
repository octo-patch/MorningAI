# MorningAI

Daily AI news tracking **skill** that runs inside AI coding tools (Claude Code, Codex, OpenCode, Hermes, Cursor, ClawHub). Not a standalone service — no Docker, no servers. Invoked via `/morning-ai` or by reading `SKILL.md`.

## Tech Stack

- **Language**: Python 3.9+
- **Dependencies**: stdlib only — no `requirements.txt`, no `pyproject.toml`. Uses `urllib`, `json`, `xml.etree`, `smtplib`, `email.mime`, `string.Template`, `dataclasses`.
- **Distribution**: source files only. Plugin manifests for Claude Code (`.claude-plugin/`) and Codex (`.codex-plugin/`).
- **Schedule frequency**: daily at 08:00 UTC+8 (idempotent, unattended).

## Project Structure

```
SKILL.md                       # Main entry point (symlinked from skills/morning-ai/)
AGENTS.md                      # Auto-discovery for OpenCode/Hermes/Codex
.claude-plugin/                # Claude Code plugin metadata + marketplace
.codex-plugin/                 # OpenAI Codex plugin metadata
lib/                           # Shared Python modules (collectors, scoring, dedupe, IO)
skills/
├── morning-ai/                # Main orchestrator (SKILL.md is a symlink to root)
├── tracking-list/             # Step 1: Python collectors → data_{date}.json
├── leaderboard/               # Optional: leaderboard ranking diff over time
├── gen-infographic/           # Step 4: image generation (5 styles)
├── gen-social/                # Step 5: per-platform social copy (X, Xiaohongshu)
├── gen-message/               # Step 6: message digest for chat platforms
└── gen-email/                 # Step 7: SMTP email subscription
entities/                      # 80+ tracked entities organized by group (markdown tables)
templates/                     # Report templates
docs/                          # Style previews, email setup guide, etc.
tests/                         # Unit tests (stdlib unittest)
```

## Pipeline

All sub-skills consume the same `data_{YYYY-MM-DD}.json` produced by Step 1, so each output channel sees identical scored / deduped / verified items.

```
collect.py (Step 1) → data_{date}.json
  → tracking-list/SKILL.md (Step 2: spec for AI agent)
  → report_{date}.md (Step 3: structured report)
  → gen-infographic/ (Step 4, optional: cover + per-type images)
  → gen-social/ (Step 5, optional: per-platform copy)
  → gen-message/ (Step 6, optional: chat digest)
  → gen-email/ (Step 7, optional: SMTP delivery)
```

## Configuration

Loaded by `lib/env.py` in this priority order (later overrides earlier):

1. `~/.config/morning-ai/.env` (global)
2. `.claude/morning-ai.env` (project)
3. `.env` (project, gitignored)
4. `.env.local` (local-only)
5. Environment variables matching prefixes: `MORNING_AI_`, `GITHUB_`, `IMAGE_GEN_`, `IMAGE_STYLE`, `GEMINI_`, `MINIMAX_`, `SOCIAL_`, `MESSAGE_`, `EMAIL_`

When extending with a new feature, add its env-var prefix to the whitelist tuple in `lib/env.py:get_config()`.

## Output Files (date-stamped, gitignored)

| Pattern | Producer | Notes |
|---------|----------|-------|
| `data_{date}.json` | tracking-list/collect.py | Source of truth for all downstream skills |
| `report_{date}.md` | morning-ai (Step 3) | Detailed daily report |
| `manifest_{date}.json` | gen-infographic | Image generation jobs |
| `social/{date}_*.md` | gen-social | Per-platform copy |
| `message_{date}.md` / `.png` | gen-message | Chat digest |
| `email_{date}.html` / `.txt` | gen-email | Local previews of sent emails |
| `email_{date}_manifest.json` | gen-email | Per-recipient send status |

## Key Conventions

- **Skill versioning**: bump every `version: "x.y.z"` field in `SKILL.md`s + `plugin.json`s + `marketplace.json` together. Add a CHANGELOG entry.
- **Symlink**: `skills/morning-ai/SKILL.md` is a symlink to root `SKILL.md` so Claude Code's skill scanner finds it. Edit the root file — both paths show the same content.
- **Date convention**: `YYYY-MM-DD` in UTC+8 (Asia/Shanghai). The 24-hour collection window is `08:00 UTC+8 yesterday` → `08:00 UTC+8 today`.
- **Sub-skill activation**: each optional output channel is gated by an `*_ENABLED=true` env var (`MESSAGE_ENABLED`, `SOCIAL_ENABLED`, `EMAIL_ENABLED`). Steps silently no-op when their gate is unset.
- **Script entry pattern**: scripts under `skills/*/scripts/` add `sys.path.insert(0, str(Path(__file__).resolve().parents[3]))` to import `lib`.
- **Stdlib only**: do not introduce external dependencies. The project's portability across AI tool environments depends on this — anything more than `python3` is friction.

## Testing

```bash
python3 -m unittest discover tests -v
```

For end-to-end checks of an output channel, prefer dry-run modes (e.g. `EMAIL_DRY_RUN=true`) over hitting real services.
