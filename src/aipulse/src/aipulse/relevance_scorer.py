"""
Cross-digest relevance and topic consistency scorer.

Identifies which news items represent persistent themes versus one-off events
by computing topic similarity and tracking recurrence across time windows.
"""

from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict
import math

@dataclass
class CosineSimilarityScorer:
    """Computes cosine similarity between news summaries."""

    def tokenize(self, text):
        """Simple lowercase word tokenization."""
        return set(w.lower() for w in text.split() if len(w) > 2)

    def cosine_similarity(self, text1, text2):
        """Compute cosine similarity between two texts."""
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0
        intersection = len(tokens1 & tokens2)
        denom = math.sqrt(len(tokens1) * len(tokens2))
        return intersection / denom if denom > 0 else 0.0

@dataclass
class PersistenceTracker:
    """Tracks theme prevalence across time windows."""
    items = field(default_factory=list)

    def add_item(self, headline, category, date):
        """Add an item to tracking."""
        self.items.append({"headline": headline, "category": category, "date": date})

    def theme_frequency(self, days=7):
        """Count items by category in the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [it for it in self.items if it["date"] >= cutoff]
        return Counter(it["category"] for it in recent)

def rank_by_relevance(digests, scorer=None):
    """Rank items across digests by topic consistency and recurrence."""
    if scorer is None:
        scorer = CosineSimilarityScorer()

    ranked = []
    tracker = PersistenceTracker()

    for digest in digests:
        freq = tracker.theme_frequency(7)
        for item in digest.items:
            tracker.add_item(item.headline, item.category, digest.day)
            relevance = freq.get(item.category, 0) / max(len(digest.items), 1)
            ranked.append((item, relevance, item.category))

    return sorted(ranked, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    from datetime import date

    class MockItem:
        def __init__(self, headline, category):
            self.headline = headline
            self.category = category

    class MockDigest:
        def __init__(self, day, items):
            self.day = day
            self.items = items

    items1 = [
        MockItem("AI Model Released", "models"),
        MockItem("GPU Shortage", "chips"),
        MockItem("Safety Regulation", "policy"),
    ]
    items2 = [
        MockItem("New AI Training Technique", "models"),
        MockItem("Memory Constraints Ease", "chips"),
        MockItem("AI Bill Passed", "policy"),
    ]

    d1 = MockDigest(date(2026, 9, 29), items1)
    d2 = MockDigest(date(2026, 9, 30), items2)

    ranked = rank_by_relevance([d1, d2])
    for item, score, cat in ranked[:5]:
        print(f"{item.headline} (score={score:.2f}, cat={cat})")
