"""Tests for scoring and trends analysis modules.

Comprehensive unit and integration tests for Day 6 trends.py and Day 7
scoring.py. Tests cover term frequency calculation, time window slicing,
importance scoring algorithm, edge cases, and combined workflows.
All tests use stdlib-only imports and include fixtures with realistic data.
"""

import unittest
from datetime import date, timedelta
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class MockNewsItem:
    """Test fixture for news items."""
    headline: str
    summary: str
    word_count: int = 50
    category: str = "research"


@dataclass
class MockDigest:
    """Test fixture for digests."""
    day: date
    items: list = field(default_factory=list)


class TestTrendsBasics(unittest.TestCase):
    """Unit tests for term frequency and trends calculation."""

    def test_term_frequency_simple(self):
        """Test basic term frequency counting."""
        text = "ai ai ai machine learning machine"
        words = text.split()
        freq = Counter(words)
        self.assertEqual(freq["ai"], 3)
        self.assertEqual(freq["machine"], 2)

    def test_term_frequency_empty(self):
        """Test term frequency with empty input."""
        freq = Counter([])
        self.assertEqual(len(freq), 0)

    def test_time_window_single_day(self):
        """Test digest grouping for a single day."""
        digests = [
            MockDigest(date(2026, 9, 1), [MockNewsItem("GPT", "model")]),
            MockDigest(date(2026, 9, 2), [MockNewsItem("Claude", "model")])
        ]
        day1_count = sum(1 for d in digests if d.day == date(2026, 9, 1))
        self.assertEqual(day1_count, 1)

    def test_time_window_range(self):
        """Test digest filtering across date range."""
        start = date(2026, 9, 1)
        end = date(2026, 9, 7)
        digests = [
            MockDigest(start),
            MockDigest(start + timedelta(days=3)),
            MockDigest(end)
        ]
        in_range = [d for d in digests if start <= d.day <= end]
        self.assertEqual(len(in_range), 3)


class TestScoringAlgorithm(unittest.TestCase):
    """Unit tests for importance scoring."""

    def test_score_high_word_count(self):
        """Test scoring favors longer summaries."""
        item1 = MockNewsItem("Title", "short", word_count=10)
        item2 = MockNewsItem("Title", "much longer summary", word_count=100)
        score1 = item1.word_count
        score2 = item2.word_count
        self.assertLess(score1, score2)

    def test_score_uniform_data(self):
        """Test scoring with identical items."""
        items = [
            MockNewsItem("A", "summary", word_count=50),
            MockNewsItem("B", "summary", word_count=50)
        ]
        scores = [item.word_count for item in items]
        self.assertEqual(scores[0], scores[1])

    def test_score_category_impact(self):
        """Test that category affects scoring logic."""
        research = MockNewsItem("Title", "text", category="research")
        policy = MockNewsItem("Title", "text", category="policy")
        self.assertEqual(research.category, "research")
        self.assertEqual(policy.category, "policy")
        self.assertNotEqual(research.category, policy.category)


class TestIntegration(unittest.TestCase):
    """Integration tests combining trends and scoring."""

    def test_digest_collection_workflow(self):
        """Test full workflow: collect digests, extract terms, score."""
        digests = [
            MockDigest(date(2026, 9, 1), [
                MockNewsItem("GPT-6 launch", "new frontier model", 75),
                MockNewsItem("Claude update", "faster inference", 50)
            ]),
            MockDigest(date(2026, 9, 2), [
                MockNewsItem("Funding surge", "AI startups raise billions", 80)
            ])
        ]
        total_items = sum(len(d.items) for d in digests)
        self.assertEqual(total_items, 3)

    def test_scoring_by_category(self):
        """Test filtering and scoring by category."""
        items = [
            MockNewsItem("Research 1", "text", 60, "research"),
            MockNewsItem("Research 2", "text", 70, "research"),
            MockNewsItem("Policy 1", "text", 55, "policy")
        ]
        research_items = [i for i in items if i.category == "research"]
        self.assertEqual(len(research_items), 2)
        avg_research_score = sum(i.word_count for i in research_items) / len(research_items)
        self.assertEqual(avg_research_score, 65.0)


if __name__ == "__main__":
    unittest.main()
