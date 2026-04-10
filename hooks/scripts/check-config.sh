#!/usr/bin/env bash
# morning-ai configuration check — runs on session start
set -euo pipefail

PROJECT_ENV=".claude/morning-ai.env"
GLOBAL_ENV="$HOME/.config/morning-ai/.env"

# Find active config
ACTIVE_ENV=""
if [[ -f "$PROJECT_ENV" ]]; then
    ACTIVE_ENV="$PROJECT_ENV"
elif [[ -f ".env" ]]; then
    ACTIVE_ENV=".env"
elif [[ -f "$GLOBAL_ENV" ]]; then
    ACTIVE_ENV="$GLOBAL_ENV"
fi

# Load env if found
if [[ -n "$ACTIVE_ENV" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ACTIVE_ENV" 2>/dev/null || true
    set +a
fi

# ── No config found: first-time onboarding ──────────────────────────────
if [[ -z "$ACTIVE_ENV" ]]; then
    cat <<'WELCOME'
morning-ai: First-time setup

What is morning-ai?
  AI news daily report generator. Tracks 80+ entities (OpenAI, Anthropic,
  Google, Meta, xAI, DeepSeek, Cursor, Midjourney, etc.) across 9 data
  sources. Generates scored, deduplicated Markdown reports with optional
  infographics. Runs as a skill inside your AI coding agent.

FREE sources (work immediately, no keys needed):
  Reddit            public JSON API
  Hacker News       Algolia API
  HuggingFace       public API
  arXiv             public API

API keys (optional, unlock more sources):
  SCRAPECREATORS_API_KEY   X/Twitter search       https://scrapecreators.com
  GITHUB_TOKEN             GitHub releases         https://github.com/settings/tokens
  YOUTUBE_API_KEY          YouTube channels        https://console.cloud.google.com
  DISCORD_TOKEN            Discord announcements   https://discord.com/developers

Image generation (optional):
  IMAGE_GEN_PROVIDER       gemini | minimax | none (default: none)
  IMAGE_STYLE              classic | dark | glassmorphism | newspaper | tech
  GEMINI_API_KEY           Google Gemini/Imagen    https://aistudio.google.com/apikey
  MINIMAX_API_KEY          MiniMax global          https://www.minimax.io
  MINIMAX_API_KEY          MiniMax cn              https://platform.minimaxi.com

Setup:
  Create ~/.config/morning-ai/.env with KEY=value format (one per line).
  You can start with zero keys (4/9 sources) and add more later.

Next: run /morning-ai
WELCOME
    exit 0
fi

# ── Config exists: show source status ────────────────────────────────────
SOURCES=4  # Reddit, HN, HuggingFace, arXiv are always free
DETAILS="reddit,hackernews,huggingface,arxiv"

if [[ -n "${SCRAPECREATORS_API_KEY:-}" ]]; then
    SOURCES=$((SOURCES + 1)); DETAILS="$DETAILS,x-twitter"
fi
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    SOURCES=$((SOURCES + 1)); DETAILS="$DETAILS,github"
fi
if [[ -n "${YOUTUBE_API_KEY:-}" ]]; then
    SOURCES=$((SOURCES + 1)); DETAILS="$DETAILS,youtube"
fi
if [[ -n "${DISCORD_TOKEN:-}" ]]; then
    SOURCES=$((SOURCES + 1)); DETAILS="$DETAILS,discord"
fi

IMG=""
if [[ -n "${IMAGE_GEN_PROVIDER:-}" && "${IMAGE_GEN_PROVIDER:-}" != "none" ]]; then
    IMG=" | image: ${IMAGE_GEN_PROVIDER}"
fi

echo "morning-ai: $SOURCES/8 sources active [$DETAILS]${IMG} (config: $ACTIVE_ENV)"
