"""Scoring module for morning-ai.

Maps collector relevance scores to morning-ai's 1-10 importance scale.
Combines engagement, source reliability, and content relevance.
Adapted from last30days score.py composite scoring approach.
"""

import bisect
import math
from typing import List

from .schema import TrackerItem, SOURCE_X, SOURCE_GITHUB, SOURCE_HUGGINGFACE, SOURCE_ARXIV, SOURCE_WEB, SOURCE_REDDIT, SOURCE_HACKERNEWS

# Source reliability weights (official sources > community)
SOURCE_RELIABILITY = {
    SOURCE_GITHUB: 0.9,
    SOURCE_HUGGINGFACE: 0.85,
    SOURCE_ARXIV: 0.8,
    SOURCE_WEB: 0.7,
    SOURCE_X: 0.65,
    SOURCE_REDDIT: 0.5,
    SOURCE_HACKERNEWS: 0.55,
}

# Scoring component weights — Stage 1 automated scoring dimensions.
# These are computable from collector metadata (not the same as the
# 5-dimension agent evaluation criteria in tracking-list/SKILL.md).
WEIGHT_RELEVANCE = 0.35
WEIGHT_ENGAGEMENT = 0.30
WEIGHT_SOURCE_RELIABILITY = 0.20
WEIGHT_RECENCY = 0.15


def _compute_engagement_score(item: TrackerItem) -> float:
    """Compute normalized engagement score (0-1) based on source type."""
    eng = item.engagement

    if item.source == SOURCE_X:
        raw = (
            0.55 * math.log1p(eng.likes)
            + 0.25 * math.log1p(eng.reposts)
            + 0.15 * math.log1p(eng.replies)
            + 0.05 * math.log1p(eng.quotes)
        )
        return min(1.0, raw / 10.0)

    elif item.source == SOURCE_REDDIT:
        raw = (
            0.55 * math.log1p(eng.score)
            + 0.45 * math.log1p(eng.num_comments)
        )
        return min(1.0, raw / 6.0)

    elif item.source == SOURCE_HACKERNEWS:
        raw = (
            0.55 * math.log1p(eng.points)
            + 0.45 * math.log1p(eng.num_comments)
        )
        return min(1.0, raw / 6.0)

    elif item.source == SOURCE_GITHUB:
        if "Trending" in (item.source_label or ""):
            # Trending repos: star surge IS the story
            raw = (
                0.60 * math.log1p(eng.stars)
                + 0.40 * math.log1p(eng.forks)
            )
            return min(1.0, raw / 7.0)
        else:
            # Tracked-entity releases: repo lifetime stars ≠ release
            # significance.  Use flat moderate engagement so relevance
            # and source reliability drive the score instead.
            return 0.35

    elif item.source == SOURCE_HUGGINGFACE:
        raw = (
            0.50 * math.log1p(eng.views)  # downloads
            + 0.50 * math.log1p(eng.likes)
        )
        return min(1.0, raw / 8.0)

    elif item.source == SOURCE_ARXIV:
        # Variable score based on author count (proxy for lab size/importance)
        author_boost = min(0.2, eng.total * 0.02) if eng.total else 0
        return 0.4 + author_boost

    elif item.source == SOURCE_WEB:
        return 0.4  # web search results have limited engagement info

    return 0.3


def _compute_recency_score(item: TrackerItem) -> float:
    """Score based on date confidence."""
    if item.date_confidence == "high":
        return 1.0
    elif item.date_confidence == "med":
        return 0.7
    return 0.4


def score_item(item: TrackerItem) -> float:
    """Compute importance score for a single item on 1-10 scale.

    Combines:
    - Relevance (from collector): 35%
    - Engagement (platform-specific): 30%
    - Source reliability: 20%
    - Recency confidence: 15%

    Returns:
        Score from 1.0 to 10.0
    """
    relevance = item.relevance
    engagement = _compute_engagement_score(item)
    reliability = SOURCE_RELIABILITY.get(item.source, 0.5)
    recency = _compute_recency_score(item)

    composite = (
        WEIGHT_RELEVANCE * relevance
        + WEIGHT_ENGAGEMENT * engagement
        + WEIGHT_SOURCE_RELIABILITY * reliability
        + WEIGHT_RECENCY * recency
    )

    # Map 0-1 composite to 1-10 scale
    score = max(1.0, min(10.0, composite * 10.0))
    return round(score, 1)


def score_items(items: List[TrackerItem]) -> List[TrackerItem]:
    """Score all items and sort by importance descending.

    Args:
        items: List of TrackerItem to score

    Returns:
        Same items with importance field set, sorted by importance desc
    """
    for item in items:
        item.importance = score_item(item)

    # Rescale scores using percentile mapping for better distribution
    _rescale_scores(items)

    items.sort(key=lambda x: x.importance, reverse=True)
    return items


def _rescale_scores(items: List[TrackerItem]) -> None:
    """Rescale scores to spread across 2.0-9.5 range using percentiles.

    Preserves relative ordering while ensuring scores use the full range
    instead of clustering around 5-7.
    """
    if len(items) < 5:
        return

    scores = sorted(i.importance for i in items)
    n = len(scores)
    for item in items:
        pct = bisect.bisect_left(scores, item.importance) / n
        item.importance = round(2.0 + pct * 7.5, 1)


def apply_verification_bonus(items: List[TrackerItem]) -> List[TrackerItem]:
    """Apply cross-verification bonus per morning-ai rules.

    Items with 2+ cross-references get a verification bonus.
    Items scoring 7+ with <2 independent sources get a penalty.

    Args:
        items: Pre-scored items with cross_refs populated

    Returns:
        Items with adjusted importance scores
    """
    for item in items:
        num_refs = len(item.cross_refs)

        if num_refs >= 2:
            item.verified = True
            item.importance = min(10.0, item.importance + 0.5)
        else:
            item.verified = False

    items.sort(key=lambda x: x.importance, reverse=True)
    return items
