"""search.py - Ranked keyword search across the archive (Day 10).

Scores matches across headline, summary and entities using term frequency,
a recency boost and optional category/entity/date filters.

Accuracy fixes: terms were counted with str.count(), a raw substring
search, so the query "ai" matched 'said', 'chain' and 'again' and
"act" matched 'impact'. Terms are now whole-word regex matches, headline
hits count double, and recency is measured against the newest digest in
the archive (or an explicit `today`) rather than the wall clock, so
results do not silently reorder as the archive ages. The demo also passed
url and source in swapped positional order.
"""
import re

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


def search(archive: list, query: Query, today: Optional[date] = None) -> list:
    results = []
    terms = [re.compile(r"\b" + re.escape(t) + r"\b") for t in set(query.querystring.lower().split())]
    if not archive or not terms:
        return []
    today = today or max(d.day for d in archive)

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

            head, body = item.headline.lower(), item.summary.lower()
            hit_count = sum(2 * len(t.findall(head)) + len(t.findall(body)) for t in terms)
            if hit_count == 0:
                continue

            tf_score = min(hit_count * 0.1, 1.0)
            days_ago = max(0, (today - digest.day).days)
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
    d.add(NewsItem('Anthropic $965B valuation', 'Major funding round', 'source', 'https://link'))
    d.add(NewsItem('AI funding surge', 'Multiple rounds', 'source', 'https://link', Category.FUNDING))
    d.add(NewsItem('Supply chain update', 'Analysts said nothing new', 'source'))
    for r in search([d], Query('funding')) + search([d], Query('ai')):
        print(f"{r.item.headline} - {r.relevance_score:.2f} ({r.explanation})")
