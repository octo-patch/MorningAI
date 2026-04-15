"""GitHub collector for morning-ai.

Monitors releases, trending repos, and commit activity via GitHub API.
New collector — no last30days equivalent.
"""

import math
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

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
                    engagement=Engagement(),  # no repo-level stars for releases
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
