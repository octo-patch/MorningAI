"""Discord collector for morning-ai.

Monitors Discord announcement channels for new messages.
Uses Discord Bot API to read channel history.
"""

import sys
from typing import Any, Dict, List, Optional

from . import http
from .schema import TrackerItem, Engagement, CollectionResult

SOURCE_DISCORD = "discord"

DISCORD_API_BASE = "https://discord.com/api/v10"

DEPTH_CONFIG = {"quick": 10, "default": 25, "deep": 50}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[Discord] {msg}\n")
        sys.stderr.flush()


def _resolve_invite(invite_code: str, token: str) -> Optional[str]:
    """Resolve a Discord invite to get the guild/channel info."""
    url = f"{DISCORD_API_BASE}/invites/{invite_code}?with_counts=true"
    headers = {"Authorization": f"Bot {token}"}
    try:
        data = http.get(url, headers=headers, timeout=10)
        return data.get("guild", {}).get("id")
    except Exception as e:
        _log(f"Invite resolve failed for {invite_code}: {e}")
        return None


def _get_guild_channels(guild_id: str, token: str) -> List[Dict[str, Any]]:
    """Get channels in a guild, filtering for announcement/text channels."""
    url = f"{DISCORD_API_BASE}/guilds/{guild_id}/channels"
    headers = {"Authorization": f"Bot {token}"}
    try:
        channels = http.get(url, headers=headers, timeout=10)
        # Filter for announcement channels (type 5) or text channels with 'announce' in name
        return [
            c for c in channels
            if c.get("type") == 5
            or (c.get("type") == 0 and "announce" in c.get("name", "").lower())
        ]
    except Exception as e:
        _log(f"Channel list failed for guild {guild_id}: {e}")
        return []


def _get_channel_messages(
    channel_id: str,
    token: str,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """Get recent messages from a channel."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages?limit={limit}"
    headers = {"Authorization": f"Bot {token}"}
    try:
        return http.get(url, headers=headers, timeout=15)
    except Exception as e:
        _log(f"Message fetch failed for channel {channel_id}: {e}")
        return []


def _parse_date(timestamp: str) -> Optional[str]:
    """Parse Discord timestamp to YYYY-MM-DD."""
    if not timestamp:
        return None
    return timestamp[:10]


def _is_in_window(msg_date: Optional[str], from_date: str, to_date: str) -> bool:
    """Check if a message date falls within the collection window."""
    if not msg_date:
        return False
    return from_date <= msg_date <= to_date


def collect(
    channels: Dict[str, str],
    from_date: str,
    to_date: str,
    token: Optional[str],
    depth: str = "default",
) -> CollectionResult:
    """Collect Discord announcements from tracked servers.

    Args:
        channels: Dict mapping entity name -> Discord invite URL
        from_date: Start date YYYY-MM-DD
        to_date: End date YYYY-MM-DD
        token: Discord Bot token
        depth: Search depth

    Returns:
        CollectionResult
    """
    result = CollectionResult(source=SOURCE_DISCORD)

    if not token:
        result.errors.append("No DISCORD_TOKEN configured")
        return result

    msg_limit = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    all_items = []

    for entity_name, invite_url in channels.items():
        result.entities_checked += 1

        # Extract invite code from URL
        invite_code = invite_url.rstrip("/").split("/")[-1]
        guild_id = _resolve_invite(invite_code, token)
        if not guild_id:
            result.errors.append(f"Could not resolve invite for {entity_name}")
            continue

        # Find announcement channels
        ann_channels = _get_guild_channels(guild_id, token)
        if not ann_channels:
            continue

        entity_found = False
        for channel in ann_channels[:3]:  # Check up to 3 announcement channels
            messages = _get_channel_messages(channel["id"], token, msg_limit)
            if not messages:
                continue

            for msg in messages:
                msg_date = _parse_date(msg.get("timestamp", ""))
                if not _is_in_window(msg_date, from_date, to_date):
                    continue

                content = msg.get("content", "")
                if not content and msg.get("embeds"):
                    embed = msg["embeds"][0]
                    content = embed.get("description", embed.get("title", ""))

                if not content:
                    continue

                # Truncate long messages
                title = content[:100].split("\n")[0]
                summary = content[:500]

                all_items.append(TrackerItem(
                    id=f"DC-{msg['id']}",
                    title=title,
                    summary=summary,
                    entity=entity_name,
                    source=SOURCE_DISCORD,
                    source_url=f"https://discord.com/channels/{guild_id}/{channel['id']}/{msg['id']}",
                    source_label=f"{entity_name} Discord #{channel.get('name', 'announcements')}",
                    date=msg_date,
                    date_confidence="high",
                    raw_text=content,
                    engagement=Engagement(),
                    relevance=0.5,
                ))
                entity_found = True

        if entity_found:
            result.entities_with_updates += 1

    result.items = all_items
    _log(f"Collected {len(all_items)} Discord messages from {result.entities_checked} servers")
    return result
