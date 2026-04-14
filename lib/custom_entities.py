"""Entity loader for morning-ai.

Parses entity markdown files from entities/ and merges them into
platform-specific registries at runtime.

Supports three markdown formats:
  1. Standard — ``#### N. Entity Name`` headers with ``| Attribute | Info |`` tables
  2. Tabular — ``| Name | X Account | ... |`` row-per-entity tables (KOL, benchmarks)
  3. Custom  — ``## Entity Name`` headers with ``| Platform | Value |`` tables

Search paths for custom entities (first match wins):
    1. CUSTOM_ENTITIES_DIR env var
    2. ~/.config/morning-ai/entities/
    3. {project_root}/entities/custom/
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from urllib.parse import unquote_plus


# Platform field → target dict key mapping (for custom entity format)
PLATFORM_KEYS = {
    "x": "x_handles",
    "github": "github_sources",
    "huggingface": "huggingface_authors",
    "arxiv": "arxiv_queries",
    "web": "web_queries",
    "reddit": "reddit_keywords",
    "reddit_community": "reddit_subreddits",
    "hn": "hn_keywords",
}

# Attribute names that map to X handles
_X_ATTRS = {"x official account", "x account"}

# Attribute names that map to GitHub sources
_GITHUB_ATTRS = {"github", "github releases"}

# Attribute keywords that map to web_queries (blogs, changelogs, docs, etc.)
_WEB_KEYWORDS = [
    "blog", "changelog", "release notes", "research", "docs",
    "official website", "page", "volcengine", "npm package",
]

# Files to skip when loading built-in entities
_SKIP_FILES = {"custom-example.md", "trending-discovery.md"}


# ---------------------------------------------------------------------------
# Value extraction helpers
# ---------------------------------------------------------------------------

def _extract_x_handles(value: str) -> List[str]:
    """Extract X handles from markdown like ``[@OpenAI](https://x.com/OpenAI)``."""
    handles = re.findall(r'@(\w+)', value)
    return handles


def _extract_github(value: str) -> Dict[str, List[str]]:
    """Extract GitHub orgs and repos from URLs."""
    orgs: List[str] = []
    repos: List[str] = []
    for match in re.finditer(r'github\.com/([^/\s\)]+)(?:/([^/\s\)]+))?', value):
        org = match.group(1)
        repo_name = match.group(2)
        if repo_name and repo_name not in ("releases", "blob", "tree", "wiki", "issues", "pulls"):
            repo = f"{org}/{repo_name}"
            if repo not in repos:
                repos.append(repo)
        else:
            if org not in orgs:
                orgs.append(org)
    return {"orgs": orgs, "repos": repos}


def _extract_hf_authors(value: str) -> List[str]:
    """Extract HuggingFace author/org from URLs like ``huggingface.co/google``."""
    authors = []
    for match in re.finditer(r'huggingface\.co/([^/\s\)]+)', value):
        name = match.group(1)
        if name not in ("spaces", "papers", "datasets", "models"):
            authors.append(name)
    return authors


def _extract_arxiv_queries(value: str) -> List[str]:
    """Extract arXiv search queries from URLs or plain text."""
    queries = []
    for match in re.finditer(r'query=([^&\s\)]+)', value):
        queries.append(unquote_plus(match.group(1)))
    return queries


def _urls_to_site_queries(value: str) -> List[str]:
    """Convert URLs to ``site:`` search queries."""
    queries = []
    for match in re.finditer(r'https?://(?:www\.)?([^\s\)]+)', value):
        url = match.group(1).rstrip("/,.")
        # Skip repo-level GitHub/HF/arXiv URLs (handled by dedicated extractors)
        # But keep deep-path GitHub URLs (blob/tree/wiki — these are web content)
        if url.startswith("github.com"):
            parts = url.split("/")
            if len(parts) <= 3:  # github.com/org or github.com/org/repo
                continue
        if url.startswith("huggingface.co") or url.startswith("arxiv.org"):
            continue
        queries.append(f"site:{url}")
    return queries


def _parse_multi(value: str) -> List[str]:
    """Split comma-separated value and strip whitespace."""
    return [v.strip() for v in value.split(",") if v.strip()]


def _extract_subreddits(value: str) -> List[str]:
    """Extract subreddit names from Reddit Community field.

    Handles formats like:
      - [r/DeepSeek](https://www.reddit.com/r/DeepSeek/)
      - r/DeepSeek
      - https://www.reddit.com/r/DeepSeek/
    """
    subs = []
    for match in re.finditer(r'r/(\w+)', value):
        sub = match.group(1)
        if sub not in subs:
            subs.append(sub)
    return subs


def _parse_x_handles_custom(value: str) -> List[str]:
    """Parse X handles from custom format, stripping @ prefix."""
    return [h.lstrip("@") for h in _parse_multi(value)]


def _parse_github_custom(value: str) -> Dict[str, List[str]]:
    """Parse GitHub value from custom format into orgs and repos."""
    orgs = []
    repos = []
    for item in _parse_multi(value):
        if "/" in item:
            repos.append(item)
        else:
            orgs.append(item)
    return {"orgs": orgs, "repos": repos}


# ---------------------------------------------------------------------------
# Built-in entity format parser (Attribute | Info tables)
# ---------------------------------------------------------------------------

def _classify_attr(attr: str) -> str:
    """Map an attribute name to a platform key or 'skip'."""
    lower = attr.lower().strip("* ")

    # Exact matches first
    if lower in _X_ATTRS:
        return "x"
    if lower.startswith("x official account"):  # handles "(Suno)", "(Udio)" suffixes
        return "x"
    if lower in _GITHUB_ATTRS or lower.startswith("github"):
        return "github"
    if lower == "huggingface":
        return "huggingface"
    if lower == "arxiv":
        return "arxiv"
    if lower == "key people":
        return "key_people"
    if lower == "reddit keywords":
        return "reddit"
    if lower == "reddit community":
        return "reddit_community"
    if lower == "hn keywords":
        return "hn"

    # Web query keywords
    for kw in _WEB_KEYWORDS:
        if kw in lower:
            return "web"

    return "skip"


def parse_builtin_file(path: Path) -> Dict[str, Dict[str, Any]]:
    """Parse a built-in entity file with ``| Attribute | Info |`` format.

    Also handles tabular sections (``| Name | X Account | ... |``).
    """
    result = {key: {} for key in PLATFORM_KEYS.values()}
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect entity header: ### N. Name or #### N. Name
        header_match = re.match(r'^#{2,4}\s+(?:\d+\.\s+)?(.+)', line)
        if header_match:
            raw_name = header_match.group(1).strip()
            # Strip suffixes like "(Full Line)"
            raw_name = re.sub(r'\s*\(Full Line\)\s*$', '', raw_name)
            entity_name = raw_name.strip()

            # Check if next non-empty lines contain a table
            i += 1
            # Look ahead for table
            while i < len(lines) and not lines[i].strip():
                i += 1

            if i < len(lines) and lines[i].strip().startswith("|"):
                # Detect table type by header row
                header_row = lines[i].strip()
                cols = [c.strip() for c in header_row.split("|") if c.strip()]

                if len(cols) >= 2 and cols[0].lower() in ("attribute", "info"):
                    # Standard Attribute | Info table
                    i += 1  # skip header
                    # Skip separator row
                    if i < len(lines) and lines[i].strip().startswith("|--"):
                        i += 1
                    # Parse rows
                    while i < len(lines) and lines[i].strip().startswith("|"):
                        row = lines[i].strip()
                        parts = [p.strip() for p in row.split("|")]
                        parts = [p for p in parts if p]
                        if len(parts) >= 2 and not parts[0].startswith("--"):
                            attr_name = parts[0].strip("* ")
                            attr_value = parts[1]
                            _store_attr(result, entity_name, attr_name, attr_value)
                        i += 1

                elif len(cols) >= 2 and cols[0].lower() == "name":
                    # Tabular format: Name | X Account | ... (multiple entities)
                    col_headers = [c.lower().strip("* ") for c in cols]
                    i += 1
                    if i < len(lines) and lines[i].strip().startswith("|--"):
                        i += 1
                    while i < len(lines) and lines[i].strip().startswith("|"):
                        row = lines[i].strip()
                        parts = [p.strip() for p in row.split("|")]
                        parts = [p for p in parts if p]
                        if len(parts) >= 2 and not parts[0].startswith("--"):
                            row_name = parts[0].strip()
                            _store_tabular_row(result, row_name, col_headers, parts)
                        i += 1
                else:
                    i += 1
            continue

        # Also detect standalone tabular sections (no entity header, like benchmarks)
        if line.strip().startswith("|"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2 and cols[0].lower() == "name":
                col_headers = [c.lower().strip("* ") for c in cols]
                i += 1
                if i < len(lines) and lines[i].strip().startswith("|--"):
                    i += 1
                while i < len(lines) and lines[i].strip().startswith("|"):
                    row = lines[i].strip()
                    parts = [p.strip() for p in row.split("|")]
                    parts = [p for p in parts if p]
                    if len(parts) >= 2 and not parts[0].startswith("--"):
                        row_name = parts[0].strip()
                        _store_tabular_row(result, row_name, col_headers, parts)
                    i += 1
                continue

        i += 1

    return result


def _store_attr(result: dict, entity: str, attr_name: str, value: str):
    """Store a single attribute value into the appropriate registry."""
    platform = _classify_attr(attr_name)

    if platform == "x":
        handles = _extract_x_handles(value)
        if handles:
            result["x_handles"].setdefault(entity, []).extend(handles)
    elif platform == "key_people":
        # Extract X handles from Key People field
        handles = _extract_x_handles(value)
        if handles:
            result["x_handles"].setdefault(entity, []).extend(handles)
    elif platform == "github":
        gh = _extract_github(value)
        existing = result["github_sources"].get(entity, {"orgs": [], "repos": []})
        existing["orgs"].extend(o for o in gh["orgs"] if o not in existing["orgs"])
        existing["repos"].extend(r for r in gh["repos"] if r not in existing["repos"])
        result["github_sources"][entity] = existing
    elif platform == "huggingface":
        authors = _extract_hf_authors(value)
        if authors:
            result["huggingface_authors"].setdefault(entity, []).extend(authors)
    elif platform == "arxiv":
        queries = _extract_arxiv_queries(value)
        if queries:
            result["arxiv_queries"].setdefault(entity, []).extend(queries)
    elif platform == "web":
        queries = _urls_to_site_queries(value)
        if queries:
            result["web_queries"].setdefault(entity, []).extend(queries)
    elif platform == "reddit":
        keywords = _parse_multi(value)
        if keywords:
            result["reddit_keywords"][entity] = keywords
    elif platform == "reddit_community":
        subs = _extract_subreddits(value)
        if subs:
            result["reddit_subreddits"].setdefault(entity, []).extend(
                s for s in subs if s not in result["reddit_subreddits"].get(entity, [])
            )
    elif platform == "hn":
        keywords = _parse_multi(value)
        if keywords:
            result["hn_keywords"][entity] = keywords


def _store_tabular_row(result: dict, name: str, col_headers: List[str], parts: List[str]):
    """Store a row from a tabular entity table (Name | X Account | ...)."""
    for idx, header in enumerate(col_headers):
        if idx >= len(parts):
            break
        value = parts[idx]
        if not value or value == "-":
            continue

        if header in ("x account",):
            handles = _extract_x_handles(value)
            if handles:
                result["x_handles"].setdefault(name, []).extend(handles)
        elif header == "github":
            gh = _extract_github(value)
            existing = result["github_sources"].get(name, {"orgs": [], "repos": []})
            existing["orgs"].extend(o for o in gh["orgs"] if o not in existing["orgs"])
            existing["repos"].extend(r for r in gh["repos"] if r not in existing["repos"])
            result["github_sources"][name] = existing
        elif header == "website":
            queries = _urls_to_site_queries(value)
            if queries:
                result["web_queries"].setdefault(name, []).extend(queries)


# ---------------------------------------------------------------------------
# Built-in entity loader
# ---------------------------------------------------------------------------

def load_builtin_entities() -> Dict[str, Dict[str, Any]]:
    """Load all built-in entity files from ``entities/`` directory.

    Returns:
        Merged dictionary with keys matching PLATFORM_KEYS values.
    """
    merged = {key: {} for key in PLATFORM_KEYS.values()}
    entities_dir = Path(__file__).resolve().parent.parent / "entities"

    if not entities_dir.is_dir():
        return merged

    for md_file in sorted(entities_dir.glob("*.md")):
        if md_file.name in _SKIP_FILES:
            continue
        if md_file.name.startswith("custom"):
            continue
        try:
            parsed = parse_builtin_file(md_file)
            for dict_key in PLATFORM_KEYS.values():
                for entity, values in parsed[dict_key].items():
                    if dict_key in ("github_sources",):
                        existing = merged[dict_key].get(entity, {"orgs": [], "repos": []})
                        existing["orgs"].extend(o for o in values["orgs"] if o not in existing["orgs"])
                        existing["repos"].extend(r for r in values["repos"] if r not in existing["repos"])
                        merged[dict_key][entity] = existing
                    elif isinstance(values, list):
                        merged[dict_key].setdefault(entity, []).extend(
                            v for v in values if v not in merged[dict_key].get(entity, [])
                        )
                    else:
                        merged[dict_key][entity] = values
        except Exception as e:
            print(f"[morning-ai] Warning: failed to parse {md_file}: {e}", file=sys.stderr)

    return merged


# ---------------------------------------------------------------------------
# Custom entity format parser (Platform | Value tables)
# ---------------------------------------------------------------------------

def parse_custom_file(path: Path) -> Dict[str, Dict[str, Any]]:
    """Parse a single custom entity markdown file.

    Returns:
        Dict with keys matching PLATFORM_KEYS values, each mapping
        entity names to their platform-specific values.
    """
    result = {key: {} for key in PLATFORM_KEYS.values()}

    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^## +", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        entity_name = lines[0].strip()
        if not entity_name:
            continue

        for line in lines[1:]:
            line = line.strip()
            if not line.startswith("|") or line.startswith("|--") or line.startswith("| Platform"):
                continue
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]
            if len(parts) < 2:
                continue

            platform = parts[0].lower().strip("*")
            value = parts[1]

            if platform == "x":
                result["x_handles"][entity_name] = _parse_x_handles_custom(value)
            elif platform == "github":
                result["github_sources"][entity_name] = _parse_github_custom(value)
            elif platform == "huggingface":
                result["huggingface_authors"][entity_name] = _parse_multi(value)
            elif platform == "arxiv":
                result["arxiv_queries"][entity_name] = _parse_multi(value)
            elif platform == "web":
                result["web_queries"][entity_name] = _parse_multi(value)
            elif platform == "reddit":
                result["reddit_keywords"][entity_name] = _parse_multi(value)
            elif platform in ("reddit community", "reddit_community"):
                subs = _extract_subreddits(value)
                if subs:
                    result["reddit_subreddits"][entity_name] = subs
            elif platform == "hn":
                result["hn_keywords"][entity_name] = _parse_multi(value)

    return result


def _get_search_dirs() -> List[Path]:
    """Get custom entity directories in priority order."""
    dirs = []
    env_dir = os.environ.get("CUSTOM_ENTITIES_DIR")
    if env_dir:
        dirs.append(Path(env_dir))
    dirs.append(Path.home() / ".config" / "morning-ai" / "entities")
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
    reddit_subreddits: dict,
    hn_keywords: dict,
) -> None:
    """Load custom entities and merge into the provided registry dicts."""
    custom = load_custom_entities()

    x_handles.update(custom["x_handles"])
    github_sources.update(custom["github_sources"])
    huggingface_authors.update(custom["huggingface_authors"])
    arxiv_queries.update(custom["arxiv_queries"])
    web_queries.update(custom["web_queries"])
    reddit_keywords.update(custom["reddit_keywords"])
    reddit_subreddits.update(custom["reddit_subreddits"])
    hn_keywords.update(custom["hn_keywords"])
