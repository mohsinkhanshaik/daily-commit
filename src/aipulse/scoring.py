"""Importance scoring for news items on a true 0-10 scale.

The first version crashed at import (it used Category.research, but the
enum members are UPPERCASE), and even with that fixed its "0-10" score
could not reach 10: category weight was added raw (0.8-1.3) instead of
scaled to its 2.0 budget, and recency was documented but never computed.

Budget (sums to exactly 10):
    depth      3.0  summary length, saturating at 60 words (digest
                    summaries are 2-3 sentences, so 150 was unreachable)
    entities   2.5  distinct companies/models, saturating at 4; entities
                    are extracted on the fly when item.entities is empty
    category   2.0  CATEGORY_WEIGHTS scaled so the top weight earns 2.0
    sourcing   1.5  1.5 with a real http(s) URL, 0.75 with a named source
    recency    1.0  linear decay to 0 over RECENCY_DAYS; full credit when
                    no dates are supplied so undated callers are not punished
"""

from datetime import date

from entities import extract_entities
from models import Category, NewsItem

CATEGORY_WEIGHTS = {
    Category.MODELS: 1.25,
    Category.RESEARCH: 1.3,
    Category.CHIPS: 1.2,
    Category.POLICY: 1.15,
    Category.FUNDING: 1.1,
    Category.PRODUCTS: 1.0,
    Category.OTHER: 0.8,
}
RECENCY_DAYS = 30
_TOP_WEIGHT = max(CATEGORY_WEIGHTS.values())


def breakdown(item: NewsItem, day: date = None, today: date = None) -> dict:
    """Per-component scores, useful for explaining a ranking."""
    entities = item.entities or extract_entities(item.headline + " " + item.summary).all()
    if item.url.startswith(("http://", "https://")):
        sourcing = 1.5
    else:
        sourcing = 0.75 if item.source else 0.0
    recency = 1.0
    if day and today:
        age = max(0, (today - day).days)
        recency = max(0.0, 1.0 - age / RECENCY_DAYS)
    return {
        "depth": round(min(item.word_count() / 60.0, 1.0) * 3.0, 3),
        "entities": round(min(len(set(entities)) / 4.0, 1.0) * 2.5, 3),
        "category": round(CATEGORY_WEIGHTS.get(item.category, 1.0) / _TOP_WEIGHT * 2.0, 3),
        "sourcing": sourcing,
        "recency": round(recency, 3),
    }


def score(item: NewsItem, day: date = None, today: date = None) -> float:
    """Importance on a 0-10 scale (see module docstring for the budget)."""
    return round(sum(breakdown(item, day, today).values()), 2)


def score_items(items, day=None, today=None):
    """Scores for a list of items, in the same order."""
    return [score(i, day, today) for i in items]


def sorted_by_importance(items, day=None, today=None):
    """Sort news items by importance score, highest first."""
    return sorted(items, key=lambda i: score(i, day, today), reverse=True)


if __name__ == "__main__":
    rich = NewsItem("OpenAI gates GPT-6 Cyber", " ".join(["word"] * 70),
                    "Reuters", "https://reuters.com/x", Category.RESEARCH,
                    ["OpenAI", "GPT-6", "Anthropic", "Nvidia"])
    thin = NewsItem("Startup note", "Short.", category=Category.OTHER)
    for it in (rich, thin):
        print("%-26s %5.2f %s" % (it.headline, score(it), breakdown(it)))
    print("old item:", score(rich, date(2026, 10, 1), date(2026, 11, 7)))
