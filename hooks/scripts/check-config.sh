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
  Google, Meta, xAI, DeepSeek, Cursor, Midjourney, etc.) across 5 automated
  sources + agent-driven X/Twitter search. Generates scored, deduplicated
  Markdown reports with optional infographics.

FREE sources (work immediately, no keys needed):
  Reddit            public JSON API
  Hacker News       Algolia API
  GitHub            public API (optional token for higher rate limits)
  HuggingFace       public API
  arXiv             public API
  X/Twitter         agent web search (no API key needed)

API keys (optional):
  GITHUB_TOKEN             GitHub higher rate limits   https://github.com/settings/tokens

Image generation (optional):
  IMAGE_GEN_PROVIDER       gemini | minimax | none (default: none)
  IMAGE_STYLE              classic | dark | glassmorphism | newspaper | tech
  GEMINI_API_KEY           Google Gemini/Imagen    https://aistudio.google.com/apikey
  MINIMAX_API_KEY          MiniMax global          https://www.minimax.io
  MINIMAX_API_KEY          MiniMax cn              https://platform.minimaxi.com

Setup:
  Create ~/.config/morning-ai/.env with KEY=value format (one per line).
  All sources work without API keys. Add GITHUB_TOKEN for higher rate limits.

Next: run /morning-ai
WELCOME
    exit 0
fi

# ── Config exists: show source status ────────────────────────────────────
SOURCES=5  # Reddit, HN, GitHub, HuggingFace, arXiv are always available
DETAILS="reddit,hackernews,github,huggingface,arxiv,x(agent-search)"

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    DETAILS="$DETAILS,github-token(enhanced)"
fi

IMG=""
if [[ -n "${IMAGE_GEN_PROVIDER:-}" && "${IMAGE_GEN_PROVIDER:-}" != "none" ]]; then
    IMG=" | image: ${IMAGE_GEN_PROVIDER}"
fi

echo "morning-ai: $SOURCES sources + X agent search [$DETAILS]${IMG} (config: $ACTIVE_ENV)"
