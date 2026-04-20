"""Environment and configuration management for morning-ai."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# Skill root search paths (priority order)
SKILL_SEARCH_PATHS: List[Optional[str]] = [
    ".",                                           # Current checkout
    os.environ.get("CLAUDE_PLUGIN_ROOT"),           # Claude Code plugin
    str(Path.home() / ".claude" / "plugins" / "marketplaces" / "MorningAI"),
    str(Path.home() / ".claude" / "skills" / "morning-ai"),
    str(Path.home() / ".agents" / "skills" / "morning-ai"),
    str(Path.home() / ".codex" / "skills" / "morning-ai"),
]


def find_skill_root() -> str:
    """Find the skill root directory by searching known install paths."""
    for p in SKILL_SEARCH_PATHS:
        if p and Path(p).is_dir() and (Path(p) / "SKILL.md").exists():
            return str(Path(p).resolve())
    return "."


def load_env_file(path: str) -> Dict[str, str]:
    """Parse a .env file into a dict."""
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        env[key] = value
    return env


def get_config() -> Dict[str, Any]:
    """Load config from environment + .env files.

    Priority: env vars > project .env > project .claude/morning-ai.env > global config
    """
    global_env = load_env_file(str(Path.home() / ".config" / "morning-ai" / ".env"))
    project_claude_env = load_env_file(".claude/morning-ai.env")
    project_env = load_env_file(".env")
    local_env = load_env_file(".env.local")

    config = {}
    config.update(global_env)
    config.update(project_claude_env)
    config.update(project_env)
    config.update(local_env)
    config.update({k: v for k, v in os.environ.items() if k.startswith(("MORNING_AI_", "GITHUB_", "IMAGE_GEN_", "IMAGE_STYLE", "GEMINI_", "MINIMAX_", "SOCIAL_", "MESSAGE_", "EMAIL_"))})

    return config


def get_key(config: Dict[str, Any], key: str) -> Optional[str]:
    """Get a config value, returning None if empty."""
    val = config.get(key, "")
    return val if val else None


def get_available_sources(config: Dict[str, Any]) -> Dict[str, bool]:
    """Check which data sources are available based on configured API keys."""
    return {
        "reddit": True,  # public JSON, no key needed
        "hackernews": True,  # Algolia API, free
        "github": bool(get_key(config, "GITHUB_TOKEN")),
        "huggingface": True,  # public API
        "arxiv": True,  # public API
    }
