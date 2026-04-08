"""YouTube collector for morning-ai (YouTube Data API v3).

Checks official YouTube channels for new video uploads within the time window.
"""

import sys
from typing import Any, Dict, List, Optional

from . import http
from .schema import TrackerItem, Engagement, CollectionResult

SOURCE_YOUTUBE = "youtube"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

DEPTH_CONFIG = {"quick": 3, "default": 5, "deep": 10}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[YouTube] {msg}\n")
        sys.stderr.flush()


def _search_channel(
    channel_id: str,
    from_date: str,
    to_date: str,
    api_key: str,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """Search for recent videos on a channel."""
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "type": "video",
        "publishedAfter": f"{from_date}T00:00:00Z",
        "publishedBefore": f"{to_date}T23:59:59Z",
        "maxResults": str(max_results),
        "key": api_key,
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{YOUTUBE_SEARCH_URL}?{query_string}"

    try:
        data = http.get(url, timeout=15)
        return data.get("items", [])
    except Exception as e:
        _log(f"Channel search failed for {channel_id}: {e}")
        return []


def _get_video_stats(
    video_ids: List[str],
    api_key: str,
) -> Dict[str, Dict[str, int]]:
    """Get view/like counts for videos."""
    if not video_ids:
        return {}

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{YOUTUBE_VIDEOS_URL}?{query_string}"

    try:
        data = http.get(url, timeout=15)
        stats = {}
        for item in data.get("items", []):
            vid = item["id"]
            s = item.get("statistics", {})
            stats[vid] = {
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "comments": int(s.get("commentCount", 0)),
            }
        return stats
    except Exception as e:
        _log(f"Stats fetch failed: {e}")
        return {}


def collect(
    channels: Dict[str, str],
    from_date: str,
    to_date: str,
    api_key: Optional[str],
    depth: str = "default",
) -> CollectionResult:
    """Collect YouTube videos from tracked channels.

    Args:
        channels: Dict mapping entity name -> YouTube channel ID
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        api_key: YouTube Data API v3 key
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_YOUTUBE)

    if not api_key:
        result.errors.append("No YOUTUBE_API_KEY configured")
        return result

    max_results = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    all_items = []

    for entity_name, channel_id in channels.items():
        result.entities_checked += 1
        videos = _search_channel(channel_id, from_date, to_date, api_key, max_results)

        if not videos:
            continue

        # Get stats for all videos
        video_ids = [v["id"]["videoId"] for v in videos if v.get("id", {}).get("videoId")]
        stats = _get_video_stats(video_ids, api_key) if video_ids else {}

        for video in videos:
            vid = video.get("id", {}).get("videoId", "")
            snippet = video.get("snippet", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")[:300]
            published = snippet.get("publishedAt", "")[:10]  # YYYY-MM-DD
            video_url = f"https://www.youtube.com/watch?v={vid}"

            video_stats = stats.get(vid, {})

            all_items.append(TrackerItem(
                id=f"YT-{vid}",
                title=title,
                summary=description,
                entity=entity_name,
                source=SOURCE_YOUTUBE,
                source_url=video_url,
                source_label=f"{entity_name} on YouTube",
                date=published,
                date_confidence="high",
                raw_text=f"{title}\n{description}",
                engagement=Engagement(
                    views=video_stats.get("views", 0),
                    likes=video_stats.get("likes", 0),
                    num_comments=video_stats.get("comments", 0),
                ),
                relevance=0.6,
            ))

        result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} YouTube videos from {result.entities_checked} channels")
    return result
