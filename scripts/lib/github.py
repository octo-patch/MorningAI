"""GitHub collector for ai-tracker.

Monitors releases, trending repos, and commit activity via GitHub API.
New collector — no last30days equivalent.
"""

import math
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, quote

from . import http
from .schema import TrackerItem, Engagement, CollectionResult, SOURCE_GITHUB

GITHUB_API = "https://api.github.com"

DEPTH_CONFIG = {"quick": 5, "default": 10, "deep": 20}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[GitHub] {msg}\n")
        sys.stderr.flush()


def _gh_headers(token: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if len(date_str) >= 10:
        return date_str[:10]
    return None


def get_org_releases(
    org: str,
    from_date: str,
    to_date: str,
    token: Optional[str] = None,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Get recent releases from an org's repos."""
    per_page = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    headers = _gh_headers(token)

    # Search for recent releases via GitHub search API
    query = f"org:{org}"
    params = urlencode({
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": str(per_page),
    })
    url = f"{GITHUB_API}/search/repositories?{params}"

    try:
        response = http.get(url, headers=headers, timeout=30)
    except Exception as e:
        _log(f"Failed to search org {org}: {e}")
        return []

    repos = response.get("items", [])
    releases = []

    for repo in repos[:per_page]:
        repo_name = repo.get("full_name", "")
        releases_url = f"{GITHUB_API}/repos/{repo_name}/releases?per_page=5"

        try:
            repo_releases = http.get(releases_url, headers=headers, timeout=15)
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
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                })

    return releases


def get_repo_releases(
    repo: str,
    from_date: str,
    to_date: str,
    token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get recent releases from a specific repo."""
    headers = _gh_headers(token)
    url = f"{GITHUB_API}/repos/{repo}/releases?per_page=10"

    try:
        response = http.get(url, headers=headers, timeout=15)
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


def search_trending(
    query: str,
    from_date: str,
    to_date: str,
    token: Optional[str] = None,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search for trending repos related to a query."""
    per_page = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    headers = _gh_headers(token)

    params = urlencode({
        "q": f"{query} created:>{from_date}",
        "sort": "stars",
        "order": "desc",
        "per_page": str(per_page),
    })
    url = f"{GITHUB_API}/search/repositories?{params}"

    try:
        response = http.get(url, headers=headers, timeout=30)
    except Exception as e:
        _log(f"Trending search '{query}' failed: {e}")
        return []

    return response.get("items", [])


def collect(
    entities: Dict[str, Dict[str, Any]],
    from_date: str,
    to_date: str,
    token: Optional[str] = None,
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
        token: GitHub token (optional, increases rate limit)
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_GITHUB)
    all_items = []

    for entity_name, sources in entities.items():
        result.entities_checked += 1
        entity_found = False

        # Check specific repos
        for repo in sources.get("repos", []):
            releases = get_repo_releases(repo, from_date, to_date, token)
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
                    engagement=Engagement(
                        stars=rel.get("stars", 0),
                        forks=rel.get("forks", 0),
                    ),
                    relevance=0.8 if not rel.get("prerelease") else 0.5,
                ))
                entity_found = True

        # Check org releases
        for org in sources.get("orgs", []):
            releases = get_org_releases(org, from_date, to_date, token, depth)
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
                    engagement=Engagement(
                        stars=rel.get("stars", 0),
                        forks=rel.get("forks", 0),
                    ),
                    relevance=0.8 if not rel.get("prerelease") else 0.5,
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} GitHub releases from {result.entities_checked} entities")
    return result
