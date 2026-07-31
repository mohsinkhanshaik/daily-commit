"""Weekly aggregates and category counts.

Computes statistics across digest collections: news counts per week,
items per category, and temporal trends. Enables tracking of content
volume and topic balance across the archive.
"""

from datetime import datetime, timedelta
from collections import Counter
from dataclasses import dataclass

@dataclass
class WeeklyStats:
    """Statistics for a single calendar week."""
    week_start: str
    item_count: int = 0
    categories: dict = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = {}

def aggregate_by_week(digests):
    """Group digests by ISO week number, return dict of week_key -> item_count."""
    weeks = {}
    for digest in digests:
        date = digest.day
        week_num = date.isocalendar()[1]
        year = date.year
        week_key = f"{year}-W{week_num:02d}"
        if week_key not in weeks:
            weeks[week_key] = 0
        weeks[week_key] += len(digest.items)
    return weeks

def category_counts(digests):
    """Count items by category across all digests."""
    counts = Counter()
    for digest in digests:
        for item in digest.items:
            counts[item.category.value] += 1
    return dict(counts)

def weekly_summary(digests):
    """Compute full weekly statistics including categories."""
    if not digests:
        return {}
    weeks = {}
    for digest in digests:
        date = digest.day
        week_num = date.isocalendar()[1]
        year = date.year
        week_key = f"{year}-W{week_num:02d}"
        if week_key not in weeks:
            weeks[week_key] = WeeklyStats(week_start=week_key)
        weeks[week_key].item_count += len(digest.items)
        for item in digest.items:
            cat = item.category.value
            if cat not in weeks[week_key].categories:
                weeks[week_key].categories[cat] = 0
            weeks[week_key].categories[cat] += 1
    return weeks

if __name__ == "__main__":
    from models import Digest, NewsItem, Category
    from datetime import date
    demo_items = [
        NewsItem("AI Model Released", "Big labs race", "Lab A", category=Category.models),
        NewsItem("Funding Announced", "500M raised", "VC", category=Category.funding),
        NewsItem("Policy Update", "New rules", "Gov", category=Category.policy),
    ]
    demo_digest = Digest(day=date(2026, 7, 31))
    demo_digest.items = demo_items
    print("Category counts:", category_counts([demo_digest]))
    print("Weekly summary:", weekly_summary([demo_digest]))
