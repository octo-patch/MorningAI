"""GitHub collector for morning-ai.

Monitors releases, trending repos, and commit activity via GitHub API.
New collector — no last30days equivalent.

Auth resolution order (no token is ever read or held by this module):
    1. ``gh`` CLI present and authenticated -> shell out to ``gh api``.
       ``gh`` resolves its own credentials (``GH_TOKEN``, ``GITHUB_TOKEN``,
       or stored keychain/config auth) — this module never sees the value.
    2. Otherwise -> plain unauthenticated HTTP against the public API
       (same behaviour as before, just without a token to attach).
    3. Users are never prompted to mint a Personal Access Token. A
       machine with the ``gh`` CLI already authenticated (the common case
       for a coding agent) gets the higher rate limit for free.
"""

import json
import shutil
import subprocess
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_GITHUB
from .util import log, parse_date

GITHUB_API = "https://api.github.com"

DEPTH_CONFIG = {"quick": 5, "default": 10, "deep": 20}


_log = lambda msg: log("GitHub", msg, tty_only=True)

_parse_date = parse_date

# Cached at module scope so a single collect() run only pays the
# `gh auth status` subprocess cost once, not once per repo/org.
_GH_CLI_READY: Optional[bool] = None


def _gh_cli_ready() -> bool:
    """True if the `gh` CLI is installed AND authenticated.

    Never reads or returns a credential — just a yes/no. Result is cached
    per-process; a `gh auth login`/`logout` mid-run won't be picked up,
    which is an acceptable tradeoff for a collector that runs once and exits.
    """
    global _GH_CLI_READY
    if _GH_CLI_READY is not None:
        return _GH_CLI_READY
    if not shutil.which("gh"):
        _GH_CLI_READY = False
        return False
    try:
        proc = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True, timeout=5, check=False,
        )
        _GH_CLI_READY = proc.returncode == 0
    except Exception:
        _GH_CLI_READY = False
    return _GH_CLI_READY


def _gh_api_json(path_and_query: str) -> Any:
    """Run `gh api <path_and_query>` and return the parsed JSON, or None on failure.

    `gh` handles auth, rate limiting, and retries internally — no header or
    token plumbing needed here. Never logs the command's stderr verbatim
    (it can echo request URLs, not credentials, but keep output terse).
    """
    try:
        proc = subprocess.run(
            ["gh", "api", path_and_query],
            capture_output=True, timeout=30, check=False, text=True,
        )
    except Exception as e:
        _log(f"gh api {path_and_query} failed to run: {e}")
        return None
    if proc.returncode != 0:
        _log(f"gh api {path_and_query} exited {proc.returncode}")
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        _log(f"gh api {path_and_query} returned non-JSON output: {e}")
        return None


def get_org_releases(
    org: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Get recent releases from an org's repos."""
    per_page = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])

    query = f"org:{org}"
    params = urlencode({
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": str(per_page),
    })

    if _gh_cli_ready():
        response = _gh_api_json(f"search/repositories?{params}")
        if response is None:
            _log(f"Failed to search org {org} via gh api")
            return []
    else:
        url = f"{GITHUB_API}/search/repositories?{params}"
        try:
            response = http.get(url, timeout=30)
        except Exception as e:
            _log(f"Failed to search org {org}: {e}")
            return []

    repos = response.get("items", [])
    releases = []

    for repo in repos[:per_page]:
        repo_name = repo.get("full_name", "")

        if _gh_cli_ready():
            repo_releases = _gh_api_json(f"repos/{repo_name}/releases?per_page=5")
            if repo_releases is None:
                continue
        else:
            releases_url = f"{GITHUB_API}/repos/{repo_name}/releases?per_page=5"
            try:
                repo_releases = http.get(releases_url, timeout=15)
            except Exception:
                continue

        if not isinstance(repo_releases, list):
            continue

        for rel in repo_releases:
            pub_date = _parse_date(rel.get("published_at"))
            if pub_date and from_date <= pub_date <= to_date:
                releases.append({
                    "repo": repo_name,
                    "tag": rel.get("tag_name", ""),
                    "name": rel.get("name", ""),
                    "body": rel.get("body", ""),
                    "url": rel.get("html_url", ""),
                    "date": pub_date,
                    "prerelease": rel.get("prerelease", False),
                })

    return releases


def get_repo_releases(
    repo: str,
    from_date: str,
    to_date: str,
) -> List[Dict[str, Any]]:
    """Get recent releases from a specific repo."""
    if _gh_cli_ready():
        response = _gh_api_json(f"repos/{repo}/releases?per_page=10")
        if response is None:
            _log(f"Failed to get releases for {repo} via gh api")
            return []
    else:
        url = f"{GITHUB_API}/repos/{repo}/releases?per_page=10"
        try:
            response = http.get(url, timeout=15)
        except Exception as e:
            _log(f"Failed to get releases for {repo}: {e}")
            return []

    if not isinstance(response, list):
        return []

    releases = []
    for rel in response:
        pub_date = _parse_date(rel.get("published_at"))
        if pub_date and from_date <= pub_date <= to_date:
            releases.append({
                "repo": repo,
                "tag": rel.get("tag_name", ""),
                "name": rel.get("name", ""),
                "body": (rel.get("body") or "")[:500],
                "url": rel.get("html_url", ""),
                "date": pub_date,
                "prerelease": rel.get("prerelease", False),
            })

    return releases


OSSINSIGHT_API = "https://api.ossinsight.io/v1/trends/repos/"
OSSINSIGHT_DEPTH = {"quick": 20, "default": 50, "deep": 100}


def fetch_ossinsight_trending(depth: str = "default") -> List[Dict[str, Any]]:
    """Fetch trending repos from OSS Insight API (past 24 hours).

    Returns rows sorted by composite score (stars + forks + PRs + pushes).
    Free API, no auth required.
    """
    limit = OSSINSIGHT_DEPTH.get(depth, 50)
    url = f"{OSSINSIGHT_API}?period=past_24_hours&language=All"

    try:
        response = http.get(url, timeout=15, retries=2)
    except Exception as e:
        _log(f"OSS Insight API failed: {e}")
        return []

    rows = response.get("data", {}).get("rows", [])
    return rows[:limit]


def collect(
    entities: Dict[str, Dict[str, Any]],
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> CollectionResult:
    """Collect GitHub data for tracked entities.

    Args:
        entities: Dict mapping entity name -> {
            "orgs": ["openai", "anthropics"],  # GitHub org names
            "repos": ["owner/repo"],           # Specific repos
        }
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        depth: Search depth

    Returns:
        CollectionResult

    No token argument: auth is resolved internally via `gh` CLI when
    present and authenticated, else unauthenticated. See module docstring.
    """
    result = CollectionResult(source=SOURCE_GITHUB)
    all_items = []

    for entity_name, sources in entities.items():
        result.entities_checked += 1
        entity_found = False

        # Check specific repos
        for repo in sources.get("repos", []):
            releases = get_repo_releases(repo, from_date, to_date)
            for rel in releases:
                tag = rel.get("tag", "")
                name = rel.get("name") or tag
                body = rel.get("body", "")

                all_items.append(TrackerItem(
                    id=f"GH-{repo}-{tag}",
                    title=f"{repo} {name}",
                    summary=body[:300] if body else f"New release: {name}",
                    entity=entity_name,
                    source=SOURCE_GITHUB,
                    source_url=rel.get("url", f"https://github.com/{repo}/releases"),
                    source_label=f"GitHub {repo}",
                    date=rel.get("date"),
                    date_confidence="high",
                    raw_text=body,
                    engagement=Engagement(),  # no repo-level stars for releases
                    relevance=0.8 if not rel.get("prerelease") else 0.5,
                ))
                entity_found = True

        # Check org releases
        for org in sources.get("orgs", []):
            releases = get_org_releases(org, from_date, to_date, depth)
            for rel in releases:
                tag = rel.get("tag", "")
                name = rel.get("name") or tag
                repo = rel.get("repo", org)
                body = rel.get("body", "")

                all_items.append(TrackerItem(
                    id=f"GH-{repo}-{tag}",
                    title=f"{repo} {name}",
                    summary=body[:300] if body else f"New release: {name}",
                    entity=entity_name,
                    source=SOURCE_GITHUB,
                    source_url=rel.get("url", f"https://github.com/{repo}"),
                    source_label=f"GitHub {repo}",
                    date=rel.get("date"),
                    date_confidence="high",
                    raw_text=body,
                    engagement=Engagement(),  # no repo-level stars for releases
                    relevance=0.8 if not rel.get("prerelease") else 0.5,
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} GitHub releases from {result.entities_checked} entities")

    # --- OSS Insight trending: cross-verify + discover ---
    _log("Fetching OSS Insight trending repos...")
    trending_rows = fetch_ossinsight_trending(depth)

    if trending_rows:
        # Build org -> entity lookup for matching
        org_to_entity: Dict[str, str] = {}
        repo_to_entity: Dict[str, str] = {}
        for entity_name, sources in entities.items():
            for org in sources.get("orgs", []):
                org_to_entity[org.lower()] = entity_name
            for repo in sources.get("repos", []):
                repo_to_entity[repo.lower()] = entity_name

        # Score threshold: skip bottom 20% by total_score
        scores = sorted(float(r.get("total_score", 0)) for r in trending_rows)
        min_score = scores[len(scores) // 5] if len(scores) >= 5 else 0
        max_score = scores[-1] if scores else 1

        trending_count = 0
        for row in trending_rows:
            repo_name = row.get("repo_name", "")
            total_score = float(row.get("total_score", 0))

            if not repo_name or total_score < min_score:
                continue

            owner = repo_name.split("/")[0].lower() if "/" in repo_name else ""
            description = row.get("description") or ""
            stars = int(row.get("stars") or 0)
            forks = int(row.get("forks") or 0)

            # Match against tracked entities
            matched_entity = (
                org_to_entity.get(owner)
                or repo_to_entity.get(repo_name.lower())
            )

            if matched_entity:
                entity_label = matched_entity
                relevance = 0.8
            else:
                entity_label = "GitHub Trending"
                relevance = 0.6

            # Normalize OSS Insight score to 0-1 for relevance boost
            norm_score = total_score / max_score if max_score > 0 else 0
            relevance = min(1.0, relevance + norm_score * 0.15)

            all_items.append(TrackerItem(
                id=f"GH-TREND-{repo_name}",
                title=repo_name,
                summary=description[:300] if description else f"Trending repo with {stars} stars",
                entity=entity_label,
                source=SOURCE_GITHUB,
                source_url=f"https://github.com/{repo_name}",
                source_label=f"GitHub Trending (OSS Insight)",
                date=to_date,
                date_confidence="high",
                engagement=Engagement(stars=stars, forks=forks),
                relevance=relevance,
            ))
            trending_count += 1

        result.items = all_items
        _log(f"Added {trending_count} trending repos from OSS Insight")

    return result
