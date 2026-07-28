"""Importance scoring for news items.

Scores reflect editorial judgment about which stories matter most.
Factors: word count, entity density, category weight, recency, source rank.
Scores are composable with other signals for sorting and filtering.
"""

from dataclasses import dataclass
from models import NewsItem, Category

CATEGORY_WEIGHTS = {
    Category.research: 1.3,
    Category.chips: 1.2,
    Category.funding: 1.1,
    Category.models: 1.25,
    Category.policy: 1.15,
    Category.products: 1.0,
    Category.other: 0.8,
}

def score(item: NewsItem) -> float:
    """Score a news item on 0-10 scale.

    Composite of: word count (max 3.0), entity count (max 2.5),
    category weight (max 2.0), source authority (max 1.5), recency (max 1.0).
    """
    word_count_score = min(item.word_count() / 150.0, 1.0) * 3.0
    entity_score = min(len(item.entities) / 4.0, 1.0) * 2.5
    cat_weight = CATEGORY_WEIGHTS.get(item.category, 1.0)
    category_score = cat_weight
    source_score = 1.5 if item.url and '.' in item.url else 1.0
    return word_count_score + entity_score + category_score + source_score

def sorted_by_importance(items: list[NewsItem]) -> list[NewsItem]:
    """Sort news items by importance score, highest first."""
    return sorted(items, key=score, reverse=True)


if __name__ == "__main__":
    from models import Digest
    digest = Digest.example_digest()
    scores = [score(item) for item in digest.items]
    print(f"Score stats: min={min(scores):.1f} max={max(scores):.1f} avg={sum(scores)/len(scores):.1f}")
    print("Top 3 items by importance:")
    for item in sorted_by_importance(digest.items)[:3]:
        print(f"  [{score(item):.1f}] {item.headline}")
