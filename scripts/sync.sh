#!/usr/bin/env bash
# sync.sh — Deploy ai-tracker skill to multiple AI tool directories
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGETS=(
    "$HOME/.claude/skills/ai-tracker"
    "$HOME/.agents/skills/ai-tracker"
    "$HOME/.codex/skills/ai-tracker"
)

SYNC_DIRS=(scripts skills entities templates hooks)
SYNC_FILES=(SKILL.md gemini-extension.json .clawhubignore)

for target in "${TARGETS[@]}"; do
    echo "Syncing to $target ..."
    mkdir -p "$target"

    # Sync directories
    for dir in "${SYNC_DIRS[@]}"; do
        if [[ -d "$SOURCE_DIR/$dir" ]]; then
            rsync -a --delete "$SOURCE_DIR/$dir/" "$target/$dir/"
        fi
    done

    # Sync individual files
    for f in "${SYNC_FILES[@]}"; do
        if [[ -f "$SOURCE_DIR/$f" ]]; then
            cp "$SOURCE_DIR/$f" "$target/$f"
        fi
    done

    echo "  Done."
done

echo "Sync complete. Deployed to ${#TARGETS[@]} targets."
