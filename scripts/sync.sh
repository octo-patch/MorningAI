#!/usr/bin/env bash
# sync.sh — Deploy morning-ai skill to multiple AI tool directories
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TARGETS=(
    "$HOME/.claude/skills/morning-ai"
    "$HOME/.agents/skills/morning-ai"
    "$HOME/.codex/skills/morning-ai"
)

SYNC_DIRS=(lib skills entities templates hooks scripts .codex-plugin .agents .claude-plugin)
SYNC_FILES=(SKILL.md AGENTS.md gemini-extension.json .clawhubignore)

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
