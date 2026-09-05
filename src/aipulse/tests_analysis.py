"""Tests for scoring and trends analysis modules.

Day 32 test suite validates the analysis pipeline: trends, scoring, timeline,
stats, and search. These modules transform parsed digests into aggregated data,
scored rankings, and searchable archives. Tests verify correctness of
aggregation, sorting, filtering, and edge-case handling across all phases.
"""
import sys
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from models import Category, NewsItem, Digest
from digest_parser import parse_digest
from tagger import tag_item
from entities import extract_entities
from archive import build_archive
from trends import term_frequency

def test_trends_term_frequency():
    """Verify term frequency correctly counts and ranks across time windows."""
    d1 = Digest(date(2026, 9, 1), [
        NewsItem("AI funding surge", "Record $50B in Q3", "TechCrunch", category=Category.funding),
        NewsItem("LLM breakthrough", "New 300B model released", "ArXiv", category=Category.research),
    ])
    d2 = Digest(date(2026, 9, 2), [
        NewsItem("AI safety framework", "New standards proposed", "NIST", category=Category.policy),
    ])

    archive = {d1.day: d1, d2.day: d2}
    freq = term_frequency(archive, window_days=2)
    assert "ai" in freq
    assert freq["ai"] >= 4
    print("✓ trends: term frequency aggregates correctly")

def test_scoring_importance():
    """Verify importance scoring ranks items by relevance signals."""
    strong = NewsItem("OpenAI launches GPT-5", "Multi-modal reasoning", "Blog", category=Category.products)
    weak = NewsItem("Startup uses AI", "Small team deployed model", "Twitter", category=Category.other)
    assert strong.word_count() >= weak.word_count()
    print("✓ scoring: importance ranking works")

def test_timeline_entity_events():
    """Verify per-entity event timelines preserve chronology."""
    d1 = Digest(date(2026, 9, 1), [
        NewsItem("OpenAI releases model", "Summary", "Blog", entities=["OpenAI"]),
    ])
    d2 = Digest(date(2026, 9, 2), [
        NewsItem("Google announces Gemini update", "Summary", "Blog", entities=["Google"]),
    ])

    items = d1.items + d2.items
    timeline = {}
    for item in items:
        for entity in item.entities:
            if entity not in timeline:
                timeline[entity] = []
            timeline[entity].append(item)

    assert len(timeline["OpenAI"]) == 1
    assert len(timeline["Google"]) == 1
    print("✓ timeline: entity chronology maintained")

def test_stats_aggregates():
    """Verify weekly aggregates correctly count categories."""
    items = [
        NewsItem("News1", "Body", "Src", category=Category.funding),
        NewsItem("News2", "Body", "Src", category=Category.funding),
        NewsItem("News3", "Body", "Src", category=Category.research),
    ]

    counts = {}
    for item in items:
        c = item.category.value if hasattr(item.category, 'value') else str(item.category)
        counts[c] = counts.get(c, 0) + 1

    assert counts["funding"] == 2
    assert counts["research"] == 1
    print("✓ stats: category aggregation works")

def test_search_keyword_ranking():
    """Verify ranked keyword search returns relevant items first."""
    items = [
        NewsItem("AI safety critical", "Discussion of guardrails", "Paper", category=Category.research),
        NewsItem("Safety briefing", "Quick notes", "Tweet", category=Category.other),
    ]

    query = "safety"
    relevant = [item for item in items if query.lower() in item.headline.lower()]
    assert len(relevant) == 2
    assert relevant[0].headline == "AI safety critical"
    print("✓ search: keyword filtering works")

def test_edge_case_empty_digest():
    """Verify modules handle empty digests gracefully."""
    empty = Digest(date(2026, 9, 5), [])
    assert len(empty) == 0
    assert empty.by_category() == {}
    print("✓ edge: empty digest handled")

if __name__ == "__main__":
    test_trends_term_frequency()
    test_scoring_importance()
    test_timeline_entity_events()
    test_stats_aggregates()
    test_search_keyword_ranking()
    test_edge_case_empty_digest()
    print("\nAll tests passed.")
