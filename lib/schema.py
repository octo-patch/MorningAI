"""Data schema for ai-tracker items."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# AI Tracker content types (matching config.yaml)
TYPE_PRODUCT = "product"
TYPE_MODEL = "model"
TYPE_BENCHMARK = "benchmark"
TYPE_FINANCING = "financing"

VALID_TYPES = {TYPE_PRODUCT, TYPE_MODEL, TYPE_BENCHMARK, TYPE_FINANCING}

# Data source identifiers
SOURCE_X = "x"
SOURCE_REDDIT = "reddit"
SOURCE_HACKERNEWS = "hackernews"
SOURCE_GITHUB = "github"
SOURCE_HUGGINGFACE = "huggingface"
SOURCE_ARXIV = "arxiv"
SOURCE_WEB = "web"
SOURCE_YOUTUBE = "youtube"
SOURCE_DISCORD = "discord"


@dataclass
class Engagement:
    """Platform-specific engagement metrics."""
    # X/Twitter
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    quotes: int = 0
    # Reddit
    score: int = 0
    num_comments: int = 0
    upvote_ratio: float = 0.0
    # YouTube / HN
    views: int = 0
    points: int = 0
    # GitHub
    stars: int = 0
    forks: int = 0
    # General
    total: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for k, v in self.__dict__.items():
            if v:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Engagement":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class TrackerItem:
    """A single tracked update from any source."""
    id: str = ""
    title: str = ""
    summary: str = ""
    entity: str = ""  # tracked entity name, e.g. "OpenAI", "Anthropic"
    content_type: str = ""  # product | model | benchmark | financing
    source: str = ""  # x | reddit | hackernews | github | huggingface | arxiv | web
    source_url: str = ""
    source_label: str = ""  # human-readable source, e.g. "@OpenAI on X"
    date: Optional[str] = None  # YYYY-MM-DD
    date_confidence: str = "low"  # high | med | low
    raw_text: str = ""
    engagement: Engagement = field(default_factory=Engagement)
    relevance: float = 0.0  # 0-1 from collector
    importance: float = 0.0  # 1-10 ai-tracker scale (set by scoring)
    cross_refs: List[str] = field(default_factory=list)
    verified: bool = False
    verify_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "entity": self.entity,
            "content_type": self.content_type,
            "source": self.source,
            "source_url": self.source_url,
            "source_label": self.source_label,
            "date": self.date,
            "date_confidence": self.date_confidence,
            "raw_text": self.raw_text,
            "engagement": self.engagement.to_dict(),
            "relevance": self.relevance,
            "importance": self.importance,
            "cross_refs": self.cross_refs,
            "verified": self.verified,
            "verify_sources": self.verify_sources,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TrackerItem":
        engagement = Engagement.from_dict(d.get("engagement", {}))
        return cls(
            id=d.get("id", ""),
            title=d.get("title", ""),
            summary=d.get("summary", ""),
            entity=d.get("entity", ""),
            content_type=d.get("content_type", ""),
            source=d.get("source", ""),
            source_url=d.get("source_url", ""),
            source_label=d.get("source_label", ""),
            date=d.get("date"),
            date_confidence=d.get("date_confidence", "low"),
            raw_text=d.get("raw_text", ""),
            engagement=engagement,
            relevance=d.get("relevance", 0.0),
            importance=d.get("importance", 0.0),
            cross_refs=d.get("cross_refs", []),
            verified=d.get("verified", False),
            verify_sources=d.get("verify_sources", []),
        )


@dataclass
class CollectionResult:
    """Result from a single collector run."""
    source: str
    items: List[TrackerItem] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    entities_checked: int = 0
    entities_with_updates: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "items": [item.to_dict() for item in self.items],
            "errors": self.errors,
            "entities_checked": self.entities_checked,
            "entities_with_updates": self.entities_with_updates,
        }


@dataclass
class DailyReport:
    """Aggregated daily report from all sources."""
    date: str = ""
    time_window: str = ""  # e.g. "2026-04-02 08:00 ~ 2026-04-03 08:00 UTC+8"
    generated_at: str = ""
    items: List[TrackerItem] = field(default_factory=list)
    collection_results: List[CollectionResult] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "time_window": self.time_window,
            "generated_at": self.generated_at,
            "items": [item.to_dict() for item in self.items],
            "collection_results": [r.to_dict() for r in self.collection_results],
            "stats": self.stats,
        }
