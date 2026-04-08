#!/usr/bin/env bash
# ai-tracker configuration check — runs on session start
set -euo pipefail

PROJECT_ENV=".claude/ai-tracker.env"
GLOBAL_ENV="$HOME/.config/ai-tracker/.env"

# Find active config
ACTIVE_ENV=""
if [[ -f "$PROJECT_ENV" ]]; then
    ACTIVE_ENV="$PROJECT_ENV"
elif [[ -f ".env" ]]; then
    ACTIVE_ENV=".env"
elif [[ -f "$GLOBAL_ENV" ]]; then
    ACTIVE_ENV="$GLOBAL_ENV"
fi

# Count available sources
SOURCES=4  # Reddit, HN, HuggingFace, arXiv are always free

if [[ -n "$ACTIVE_ENV" ]]; then
    # Source the env file
    set -a
    # shellcheck disable=SC1090
    source "$ACTIVE_ENV" 2>/dev/null || true
    set +a
fi

# Check API keys from env
[[ -n "${SCRAPECREATORS_API_KEY:-}" ]] && SOURCES=$((SOURCES + 1))
[[ -n "${GITHUB_TOKEN:-}" ]] && SOURCES=$((SOURCES + 1))
[[ -n "${YOUTUBE_API_KEY:-}" ]] && SOURCES=$((SOURCES + 1))
[[ -n "${DISCORD_TOKEN:-}" ]] && SOURCES=$((SOURCES + 1))
[[ -n "${BRAVE_API_KEY:-}" || -n "${EXA_API_KEY:-}" ]] && SOURCES=$((SOURCES + 1))

if [[ -z "$ACTIVE_ENV" ]]; then
    echo "ai-tracker: No config found. Run /ai-tracker to set up. ($SOURCES free sources available)"
else
    echo "ai-tracker: $SOURCES/9 sources active (config: $ACTIVE_ENV)"
fi
