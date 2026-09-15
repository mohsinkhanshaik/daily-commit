"""Multi-digest aggregation and cross-source analytics.

Aggregator combines digests from multiple sources into unified views,
enabling cross-source trend tracking, deduplication across feeds, and
time-windowed analytics across repositories or external news feeds.

Design: Flat API with methods for merge, dedupe, filter, and window.
"""
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import list
from models import Digest, NewsItem


@dataclass
class AggregatedDigest:
    """A merged view of multiple source digests with metadata."""
    name: str
    source_count: int = 0
    items: list[NewsItem] = field(default_factory=list)
    date_range: tuple[str, str] = ("", "")

    def add_digest(self, digest: Digest) -> None:
        """Merge digest items and track source count."""
        self.source_count += 1
        self.items.extend(digest.items)


class Aggregator:
    """Merge and analyze digests from multiple sources."""

    def __init__(self):
        self.digests: dict[str, Digest] = {}

    def add_source(self, name: str, digest: Digest) -> None:
        """Register a digest by source name."""
        self.digests[name] = digest

    def merged(self, name: str = "merged") -> AggregatedDigest:
        """Return a merged view of all sources."""
        agg = AggregatedDigest(name=name)
        for digest in self.digests.values():
            agg.add_digest(digest)
        return agg


    def dedupe_headlines(self, min_sim: float = 0.8) -> AggregatedDigest:
        """Merge and dedupe by headline similarity (stub)."""
        agg = self.merged("deduped")
        unique_headlines = {}
        for item in agg.items:
            if item.headline not in unique_headlines:
                unique_headlines[item.headline] = item
        agg.items = list(unique_headlines.values())
        return agg

    def by_date_range(self, start: str, end: str) -> AggregatedDigest:
        """Filter merged digest to a date range."""
        agg = self.merged("windowed")
        agg.date_range = (start, end)
        agg.items = [i for i in agg.items if start <= i.headline[0:4] <= end]
        return agg


if __name__ == "__main__":
    agg = Aggregator()
    print(f"Aggregator initialized with {len(agg.digests)} sources.")
