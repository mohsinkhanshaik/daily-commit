"""Near-duplicate story detection using Jaccard similarity on headline terms.

Detects stories that cover the same event with similar wording. Compares headlines
and summaries using set intersection to find near-duplicates above a threshold.
Designed for digest deduplication before archival.
"""

from dataclasses import dataclass, field
from typing import Sequence

@dataclass
class DuplicatePair:
    """A pair of stories detected as near-duplicates."""
    headline_a: str
    headline_b: str
    similarity: float
    url_a: str = ""
    url_b: str = ""


def normalize_text(text: str) -> set:
    """Convert text to lowercase term set, filtering short words."""
    words = text.lower().split()
    return {w.strip('.,;:!?"') for w in words if len(w) > 2}


def jaccard_similarity(a: str, b: str) -> float:
    """Calculate Jaccard similarity between two text strings."""
    set_a = normalize_text(a)
    set_b = normalize_text(b)
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def find_duplicates(items: Sequence, threshold: float = 0.6) -> list:
    """Find near-duplicate stories by comparing headlines.

    Args:
        items: Sequence of items with .headline and .url attributes.
        threshold: Minimum Jaccard similarity to flag as duplicate (0.0-1.0).

    Returns:
        List of DuplicatePair objects for duplicates found.
    """
    duplicates = []
    for i, item_a in enumerate(items):
        for item_b in items[i+1:]:
            sim = jaccard_similarity(item_a.headline, item_b.headline)
            if sim >= threshold:
                duplicates.append(DuplicatePair(
                    headline_a=item_a.headline,
                    headline_b=item_b.headline,
                    similarity=round(sim, 3),
                    url_a=getattr(item_a, 'url', ''),
                    url_b=getattr(item_b, 'url', '')
                ))
    return duplicates



if __name__ == "__main__":
    from dataclasses import dataclass as dc

    @dc
    class MockItem:
        headline: str
        url: str = ""

    test_items = [
        MockItem("OpenAI releases GPT-5 model", "http://ex.com/1"),
        MockItem("OpenAI announces GPT-5 launch", "http://ex.com/2"),
        MockItem("Google DeepMind breakthrough", "http://ex.com/3"),
    ]

    dupes = find_duplicates(test_items, threshold=0.5)
    for d in dupes:
        print(f"{d.similarity}: {d.headline_a} vs {d.headline_b}")
