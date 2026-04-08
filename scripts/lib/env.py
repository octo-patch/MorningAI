"""Environment and configuration management for ai-tracker."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


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

    Priority: env vars > project .env > global .env
    """
    global_env = load_env_file(str(Path.home() / ".config" / "ai-tracker" / ".env"))
    project_env = load_env_file(".env")
    local_env = load_env_file(".env.local")

    config = {}
    config.update(global_env)
    config.update(project_env)
    config.update(local_env)
    config.update({k: v for k, v in os.environ.items() if k.startswith(("AI_TRACKER_", "SCRAPECREATORS_", "BRAVE_", "EXA_", "GITHUB_", "YOUTUBE_", "DISCORD_", "AUTH_TOKEN", "CT0"))})

    return config


def get_key(config: Dict[str, Any], key: str) -> Optional[str]:
    """Get a config value, returning None if empty."""
    val = config.get(key, "")
    return val if val else None


def get_available_sources(config: Dict[str, Any]) -> Dict[str, bool]:
    """Check which data sources are available based on configured API keys."""
    return {
        "x_bird": bool(get_key(config, "AUTH_TOKEN") and get_key(config, "CT0")),
        "x_scrapecreators": bool(get_key(config, "SCRAPECREATORS_API_KEY")),
        "reddit": True,  # public JSON, no key needed
        "hackernews": True,  # Algolia API, free
        "github": bool(get_key(config, "GITHUB_TOKEN")),
        "huggingface": True,  # public API
        "arxiv": True,  # public API
        "brave": bool(get_key(config, "BRAVE_API_KEY")),
        "exa": bool(get_key(config, "EXA_API_KEY")),
        "youtube": bool(get_key(config, "YOUTUBE_API_KEY")),
        "discord": bool(get_key(config, "DISCORD_TOKEN")),
    }
