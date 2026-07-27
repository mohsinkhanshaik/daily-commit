"""Term frequency analysis across time windows.

Exposes discourse trends by computing how term frequency evolves
across the archive. Supports time-windowed analysis, category filtering,
and growth rate calculation for rising topics.
"""

from dataclasses import dataclass, field
from collections import Counter
from datetime import date, timedelta

@dataclass
class Term:
    """A term with its frequency count."""
    text: str
    count: int

@dataclass
class TermFrequency:
    """Term frequencies for a time window."""
    start_date: date
    end_date: date
    terms: dict = field(default_factory=dict)

def term_frequency(items, min_count=2):
    """Compute term frequency across all items."""
    counter = Counter()
    for item in items:
        words = item.summary.lower().split()
        counter.update(w.strip(',.;:!?') for w in words)
    return {t: c for t, c in counter.items() if c >= min_count}

def top_terms(tf_dict, limit=10):
    """Return top N terms by frequency."""
    return sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)[:limit]

if __name__ == "__main__":
    print("Trends module loaded.")
