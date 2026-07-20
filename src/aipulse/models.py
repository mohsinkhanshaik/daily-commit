"""Core data models for AI Pulse.

Every later module (parser, tagger, scoring, trends) shares these
in-memory shapes. Stdlib-only keeps the toolkit runnable anywhere.
Category is a str Enum so items serialize to JSON without adapters.
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


@dataclass
class NewsItem:
    headline: str
    summary: str
    source: str
    url: str = ""
    category: Category = Category.OTHER
    entities: list = field(default_factory=list)

    def word_count(self):
        return len(self.summary.split())


@dataclass
class Digest:
    day: date
    items: list = field(default_factory=list)

    def add(self, item):
        self.items.append(item)

    def by_category(self, category):
        return [i for i in self.items if i.category == category]

    def __len__(self):
        return len(self.items)


if __name__ == "__main__":
    d = Digest(day=date(2026, 7, 20))
    d.add(NewsItem("Example", "Two word summary here.", "local"))
    print(len(d), "item(s);", d.items[0].word_count(), "words")
