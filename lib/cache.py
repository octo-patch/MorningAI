"""Caching utilities for morning-ai (adapted from last30days)."""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path.home() / ".cache" / "morning-ai"
DEFAULT_TTL_HOURS = 1  # short TTL for daily tracking — prevents stale cross-day cache


def ensure_cache_dir():
    global CACHE_DIR
    env_dir = os.environ.get("MORNING_AI_CACHE_DIR")
    if env_dir:
        CACHE_DIR = Path(env_dir)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        CACHE_DIR = Path(tempfile.gettempdir()) / "morning-ai" / "cache"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(source: str, entity: str, date: str) -> str:
    key_data = f"{source}|{entity}|{date}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.json"


def is_cache_valid(cache_path: Path, ttl_hours: int = DEFAULT_TTL_HOURS) -> bool:
    if not cache_path.exists():
        return False
    try:
        stat = cache_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = (now - mtime).total_seconds() / 3600
        return age_hours < ttl_hours
    except OSError:
        return False


def load_cache(cache_key: str, ttl_hours: int = DEFAULT_TTL_HOURS) -> Optional[dict]:
    cache_path = get_cache_path(cache_key)
    if not is_cache_valid(cache_path, ttl_hours):
        return None
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(cache_key: str, data: dict):
    ensure_cache_dir()
    cache_path = get_cache_path(cache_key)
    try:
        with open(cache_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass


def clear_cache():
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
            except OSError:
                pass
