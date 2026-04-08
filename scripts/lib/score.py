"""Scoring module for ai-tracker.

Maps collector relevance scores to ai-tracker's 1-10 importance scale.
Combines engagement, source reliability, and content relevance.
Adapted from last30days score.py composite scoring approach.
"""

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

# Scoring component weights (matching ai-tracker's 5-dimension system)
# Impact 30%, Differentiation 25%, Innovation 20%, Coverage 15%, Timeliness 10%
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
        return min(1.0, raw / 8.0)

    elif item.source == SOURCE_HACKERNEWS:
        raw = (
            0.55 * math.log1p(eng.points)
            + 0.45 * math.log1p(eng.num_comments)
        )
        return min(1.0, raw / 8.0)

    elif item.source == SOURCE_GITHUB:
        raw = (
            0.60 * math.log1p(eng.stars)
            + 0.40 * math.log1p(eng.forks)
        )
        return min(1.0, raw / 10.0)

    elif item.source == SOURCE_HUGGINGFACE:
        raw = (
            0.50 * math.log1p(eng.views)  # downloads
            + 0.50 * math.log1p(eng.likes)
        )
        return min(1.0, raw / 12.0)

    elif item.source == SOURCE_ARXIV:
        return 0.5  # arXiv doesn't have engagement metrics

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

    items.sort(key=lambda x: x.importance, reverse=True)
    return items


def apply_verification_bonus(items: List[TrackerItem]) -> List[TrackerItem]:
    """Apply cross-verification bonus per ai-tracker rules.

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
        elif item.importance >= 7.0 and num_refs < 2:
            # High-score items need verification per ai-tracker rules
            item.importance = max(6.9, item.importance - 0.5)
            item.verified = False

    items.sort(key=lambda x: x.importance, reverse=True)
    return items
