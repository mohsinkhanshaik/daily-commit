"""Weekly aggregates and category counts.

Fixes over the first version:
- The demo crashed with AttributeError because it used Category.models;
  enum members are UPPERCASE.
- Week keys were built from date.year plus the ISO week number. Around New
  Year those disagree: 2027-01-01 belongs to ISO week 2026-W53, but was
  keyed "2027-W53", splitting one week into two buckets (and inventing a
  week that does not exist). Keys now use the ISO year from isocalendar().
- WeeklyStats.week_start claimed to be a start date but held the week key;
  it is now the Monday of the week, and the key lives in `week`.
- aggregate_by_week and weekly_summary duplicated the bucketing loop; both
  now share week_key(), and results come back in chronological order.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta


def week_key(day: date) -> str:
    iso_year, iso_week, _ = day.isocalendar()
    return "%d-W%02d" % (iso_year, iso_week)


def week_monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


@dataclass
class WeeklyStats:
    """Statistics for one ISO week."""
    week: str
    week_start: date
    digest_count: int = 0
    item_count: int = 0
    categories: Counter = field(default_factory=Counter)

    def top_category(self):
        return self.categories.most_common(1)[0][0] if self.categories else None


def weekly_summary(digests) -> dict:
    """{week_key: WeeklyStats} in chronological order."""
    weeks = {}
    for digest in sorted(digests, key=lambda d: d.day):
        key = week_key(digest.day)
        stats = weeks.setdefault(key, WeeklyStats(key, week_monday(digest.day)))
        stats.digest_count += 1
        stats.item_count += len(digest.items)
        stats.categories.update(item.category.value for item in digest.items)
    return weeks


def aggregate_by_week(digests) -> dict:
    """{week_key: item_count}."""
    return {k: s.item_count for k, s in weekly_summary(digests).items()}


def category_counts(digests) -> dict:
    """Count items by category value across all digests."""
    counts = Counter()
    for digest in digests:
        counts.update(item.category.value for item in digest.items)
    return dict(counts.most_common())


def category_share(digests) -> dict:
    """Category -> percentage of all items, rounded to one decimal."""
    counts = category_counts(digests)
    total = sum(counts.values()) or 1
    return {cat: round(100.0 * n / total, 1) for cat, n in counts.items()}


if __name__ == "__main__":
    from models import Category, Digest, NewsItem
    a = Digest(date(2026, 12, 31), [NewsItem("Model drop", "x", category=Category.MODELS)])
    b = Digest(date(2027, 1, 1), [NewsItem("Big round", "y", category=Category.FUNDING),
                                  NewsItem("New rules", "z", category=Category.POLICY)])
    for key, s in weekly_summary([b, a]).items():
        print(key, s.week_start, s.digest_count, "digests", s.item_count, "items", dict(s.categories))
    print("Share:", category_share([a, b]))
