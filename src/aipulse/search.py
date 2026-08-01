"""

search.py - Ranked keyword search across archive (Day 10)

Implements ranked search over digest items. Scores matches across headline,
summary, entities using term frequency, recency boost, and category filtering.
Returns results sorted by relevance.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from models import Digest, NewsItem, Category


@dataclass
class Query:
    querystring: str
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    category: Optional[Category] = None
    entities: Optional[list[str]] = None


@dataclass
class RankedResult:
    item: NewsItem
    relevance_score: float
    explanation: str


def search(archive: list[Digest], query: Query) -> list[RankedResult]:
    results = []
    terms = set(query.querystring.lower().split())
    today = date.today()

    for digest in archive:
        if query.date_start and digest.day < query.date_start:
            continue
        if query.date_end and digest.day > query.date_end:
            continue

        for item in digest.items:
            if query.category and item.category != query.category:
                continue
            if query.entities and not any(e in item.entities for e in query.entities):
                continue

            text = (item.headline + ' ' + item.summary).lower()
            hit_count = sum(text.count(t) for t in terms)
            if hit_count == 0:
                continue

            tf_score = min(hit_count * 0.1, 1.0)
            days_ago = max(1, (today - digest.day).days)
            recency = 1.0 / (1.0 + days_ago * 0.05)
            relevance = tf_score * 0.7 + recency * 0.3

            results.append(RankedResult(item, relevance, f"{hit_count} hits"))

    return sorted(results, key=lambda r: r.relevance_score, reverse=True)


def by_category(results: list[RankedResult]) -> dict:
    grouped = {}
    for r in results:
        cat = r.item.category.value
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(r)
    return grouped


if __name__ == '__main__':
    d = Digest(date(2026, 8, 1))
    d.add(NewsItem('Anthropic $965B valuation', 'Major round', 'https://link', 'source'))
    d.add(NewsItem('AI funding surge', 'Multiple rounds', 'https://link', 'source', Category.FUNDING))
    q = Query('funding')
    results = search([d], q)
    for r in results:
        print(f"{r.item.headline} - {r.relevance_score:.2f}")
