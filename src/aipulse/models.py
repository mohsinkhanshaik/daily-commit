"""Core data models for AI Pulse.

Every later module (parser, tagger, scoring, trends, search, render) shares
these in-memory shapes, so this file is the contract for the whole toolkit.
Stdlib-only keeps the toolkit runnable anywhere.

Design notes:
- Category is a str Enum so items serialize to JSON without adapters.
  Members are UPPERCASE (Category.MODELS); Category.parse() accepts loose
  user input such as "Models" or "chip" and falls back to OTHER.
- NewsItem only requires a headline and a summary. Source, url, category and
  entities all have safe defaults because many producers (feeds, tests,
  demos) know only the text of a story.
- Digest.by_category() serves two callers: with a Category it returns that
  category's items (a list); with no argument it returns a dict that groups
  every non-empty category, which is what renderers and stats want.
- Digest keeps the intro line and the closing "Trend watch:" line separately
  so they never leak into a news item's summary.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Category(str, Enum):
    MODELS = "models"
    CHIPS = "chips"
    FUNDING = "funding"
    POLICY = "policy"
    RESEARCH = "research"
    PRODUCTS = "products"
    OTHER = "other"

    @classmethod
    def parse(cls, value):
        """Map loose text ("Models", "chip", Category.CHIPS) to a Category."""
        if isinstance(value, cls):
            return value
        text = str(value or "").strip().lower()
        for member in cls:
            if text in (member.value, member.value.rstrip("s")):
                return member
        return cls.OTHER


@dataclass
class NewsItem:
    headline: str
    summary: str
    source: str = ""
    url: str = ""
    category: Category = Category.OTHER
    entities: list = field(default_factory=list)

    def word_count(self):
        return len(self.summary.split())

    @property
    def text(self):
        """Headline plus summary, the text most analyzers look at."""
        return (self.headline + " " + self.summary).strip()

    def to_dict(self):
        return {
            "headline": self.headline,
            "summary": self.summary,
            "source": self.source,
            "url": self.url,
            "category": self.category.value,
            "entities": list(self.entities),
        }


@dataclass
class Digest:
    day: date
    items: list = field(default_factory=list)
    intro: str = ""
    trend_watch: str = ""

    def add(self, item):
        self.items.append(item)

    def by_category(self, category=None):
        """Items of one category (list), or all items grouped (dict)."""
        if category is not None:
            wanted = Category.parse(category)
            return [i for i in self.items if i.category == wanted]
        grouped = {}
        for item in self.items:
            grouped.setdefault(item.category, []).append(item)
        return grouped

    def to_dict(self):
        return {"day": self.day.isoformat(),
                "items": [i.to_dict() for i in self.items]}

    def __len__(self):
        return len(self.items)


if __name__ == "__main__":
    d = Digest(day=date(2026, 7, 20))
    d.add(NewsItem("Example", "Two word summary here.", "local"))
    d.add(NewsItem("Chip story", "Nvidia ships parts.", category=Category.CHIPS))
    print(len(d), "item(s);", d.items[0].word_count(), "words")
    print({c.value: len(v) for c, v in d.by_category().items()})
    print(Category.parse("Chip"), len(d.by_category("chips")))
