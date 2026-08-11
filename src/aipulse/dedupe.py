"""Near-duplicate story detection and deduplication.

Identifies similar NewsItem entries via token overlap (Jaccard similarity)
and optional fingerprinting. Merges duplicates and filters archives for
quality and novelty.
"""

import hashlib
from dataclasses import dataclass, field
from typing import List, Set

def tokenize(text: str) -> Set[str]:
    """Split text into words, lowercased and stripped."""
    return set(w.lower().strip('.,!?;:') for w in text.split() if w.strip())

def jaccard_sim(tokens_a: Set[str], tokens_b: Set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not tokens_a and not tokens_b:
        return 1.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union > 0 else 0.0

def fingerprint(text: str, bits: int = 8) -> str:
    """Simple LSH-style fingerprint: hash text and truncate."""
    h = hashlib.sha256(text.encode()).hexdigest()
    return h[:bits]

def similarity_score(item_a, item_b) -> float:
    """Score similarity between two NewsItem objects (0.0 to 1.0)."""
    tokens_a = tokenize(item_a.headline + " " + item_a.summary)
    tokens_b = tokenize(item_b.headline + " " + item_b.summary)
    return jaccard_sim(tokens_a, tokens_b)

def merge_items(primary, duplicate):
    """Merge duplicate into primary, keeping primary headline and earliest source."""
    if not primary.entities:
        primary.entities = duplicate.entities
    primary.summary = primary.summary or duplicate.summary
    return primary

def deduplicate(items: List, threshold: float = 0.7) -> List:
    """Remove near-duplicates, keeping earlier items. Returns deduplicated list."""
    if not items:
        return []
    seen_indices = set()
    result = []
    for i, item in enumerate(items):
        if i in seen_indices:
            continue
        result.append(item)
        for j in range(i + 1, len(items)):
            if j not in seen_indices:
                score = similarity_score(item, items[j])
                if score >= threshold:
                    seen_indices.add(j)
    return result
    return result

if __name__ == "__main__":
    from models import NewsItem, Category
    items = [
        NewsItem("Claude 3.5 Haiku Released", "Anthropic ships new small model variant", "AI News", "https://example.com/1", Category.RESEARCH),
        NewsItem("Anthropic Releases Haiku 3.5", "Claude Haiku 3.5 available to all users", "Tech Blog", "https://example.com/2", Category.RESEARCH),
        NewsItem("Different Story Here", "Unique research announcement from OpenAI", "OpenAI", "https://example.com/3", Category.RESEARCH),
    ]
    deduped = deduplicate(items, threshold=0.6)
    print(f"Original: {len(items)} items. Deduplicated: {len(deduped)} items.")
    for item in deduped:
        print(f"  - {item.headline}")
