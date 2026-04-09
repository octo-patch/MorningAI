"""Custom entity loader for morning-ai.

Parses user-defined entity markdown files and merges them into the
built-in entity registries at runtime.

Custom entity files use a simple format:

    ## Entity Name

    | Platform | Value |
    |----------|-------|
    | X | @handle1, @handle2 |
    | GitHub | org-name, user/repo |
    | HuggingFace | author1, author2 |

Search paths (first match wins):
    1. CUSTOM_ENTITIES_DIR env var
    2. ~/.config/morning-ai/entities/
    3. {project_root}/entities/custom/
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


# Platform field → target dict key mapping
PLATFORM_KEYS = {
    "x": "x_handles",
    "github": "github_sources",
    "huggingface": "huggingface_authors",
    "arxiv": "arxiv_queries",
    "web": "web_queries",
    "reddit": "reddit_keywords",
    "hn": "hn_keywords",
    "youtube": "youtube_channels",
    "discord": "discord_channels",
}


def _parse_multi(value: str) -> List[str]:
    """Split comma-separated value and strip whitespace."""
    return [v.strip() for v in value.split(",") if v.strip()]


def _parse_x_handles(value: str) -> List[str]:
    """Parse X handles, stripping @ prefix."""
    return [h.lstrip("@") for h in _parse_multi(value)]


def _parse_github(value: str) -> Dict[str, List[str]]:
    """Parse GitHub value into orgs and repos."""
    orgs = []
    repos = []
    for item in _parse_multi(value):
        if "/" in item:
            repos.append(item)
        else:
            orgs.append(item)
    return {"orgs": orgs, "repos": repos}


def parse_custom_file(path: Path) -> Dict[str, Dict[str, Any]]:
    """Parse a single custom entity markdown file.

    Returns:
        Dict with keys matching PLATFORM_KEYS values, each mapping
        entity names to their platform-specific values.
    """
    result = {key: {} for key in PLATFORM_KEYS.values()}

    text = path.read_text(encoding="utf-8")
    # Split by ## headings to find entity sections
    sections = re.split(r"^## +", text, flags=re.MULTILINE)

    for section in sections[1:]:  # skip content before first ##
        lines = section.strip().split("\n")
        entity_name = lines[0].strip()
        if not entity_name:
            continue

        # Find table rows (lines matching | Platform | Value |)
        for line in lines[1:]:
            line = line.strip()
            if not line.startswith("|") or line.startswith("|--") or line.startswith("| Platform"):
                continue
            # Parse | key | value |
            parts = [p.strip() for p in line.split("|")]
            # parts: ['', 'key', 'value', ''] after split
            parts = [p for p in parts if p]
            if len(parts) < 2:
                continue

            platform = parts[0].lower().strip("*")  # handle **bold** markers
            value = parts[1]

            if platform == "x":
                result["x_handles"][entity_name] = _parse_x_handles(value)
            elif platform == "github":
                result["github_sources"][entity_name] = _parse_github(value)
            elif platform == "huggingface":
                result["huggingface_authors"][entity_name] = _parse_multi(value)
            elif platform == "arxiv":
                result["arxiv_queries"][entity_name] = _parse_multi(value)
            elif platform == "web":
                result["web_queries"][entity_name] = _parse_multi(value)
            elif platform == "reddit":
                result["reddit_keywords"][entity_name] = _parse_multi(value)
            elif platform == "hn":
                result["hn_keywords"][entity_name] = _parse_multi(value)
            elif platform == "youtube":
                result["youtube_channels"][entity_name] = value.strip()
            elif platform == "discord":
                result["discord_channels"][entity_name] = value.strip()

    return result


def _get_search_dirs() -> List[Path]:
    """Get custom entity directories in priority order."""
    dirs = []

    # 1. CUSTOM_ENTITIES_DIR env var
    env_dir = os.environ.get("CUSTOM_ENTITIES_DIR")
    if env_dir:
        dirs.append(Path(env_dir))

    # 2. ~/.config/morning-ai/entities/
    dirs.append(Path.home() / ".config" / "morning-ai" / "entities")

    # 3. {project_root}/entities/custom/
    project_root = Path(__file__).resolve().parent.parent
    dirs.append(project_root / "entities" / "custom")

    return dirs


def load_custom_entities() -> Dict[str, Dict[str, Any]]:
    """Load all custom entity files from search directories.

    Returns:
        Merged dictionary of all custom entities across all files and directories.
    """
    merged = {key: {} for key in PLATFORM_KEYS.values()}

    for search_dir in _get_search_dirs():
        if not search_dir.is_dir():
            continue
        for md_file in sorted(search_dir.glob("*.md")):
            if md_file.name == "custom-example.md":
                continue
            try:
                parsed = parse_custom_file(md_file)
                for dict_key in PLATFORM_KEYS.values():
                    merged[dict_key].update(parsed[dict_key])
            except Exception as e:
                print(f"[morning-ai] Warning: failed to parse {md_file}: {e}", file=sys.stderr)

    return merged


def merge_into_registries(
    x_handles: dict,
    github_sources: dict,
    huggingface_authors: dict,
    arxiv_queries: dict,
    web_queries: dict,
    reddit_keywords: dict,
    hn_keywords: dict,
    youtube_channels: dict,
    discord_channels: dict,
) -> None:
    """Load custom entities and merge into the provided registry dicts."""
    custom = load_custom_entities()

    x_handles.update(custom["x_handles"])
    github_sources.update(custom["github_sources"])
    huggingface_authors.update(custom["huggingface_authors"])
    arxiv_queries.update(custom["arxiv_queries"])
    web_queries.update(custom["web_queries"])
    reddit_keywords.update(custom["reddit_keywords"])
    hn_keywords.update(custom["hn_keywords"])
    youtube_channels.update(custom["youtube_channels"])
    discord_channels.update(custom["discord_channels"])
