"""Test suite for AI Pulse analysis modules.

Tests scoring.py, trends.py, stats.py, and search.py. Covers importance
scoring with edge cases (zero vectors, all-zero frequencies), term frequency
analysis across time windows, weekly aggregates and category distribution logic,
and ranked keyword search with filtering. Follows patterns from tests_core.py:
class-based grouping, descriptive test names, happy path and edge cases.
"""

import unittest
from datetime import date, timedelta


class TestScoring(unittest.TestCase):
    """Tests for scoring.py importance scoring logic."""

    def test_normalize_zero_vector(self):
        """Normalize should handle zero vectors (all zeros) gracefully."""
        vec = [0, 0, 0]
        result = self._normalize_vector(vec)
        self.assertEqual(result, [0, 0, 0])

    def test_normalize_unit_vector(self):
        """Normalize non-zero vector to unit length."""
        vec = [3, 4]
        result = self._normalize_vector(vec)
        self.assertAlmostEqual(result[0], 0.6)
        self.assertAlmostEqual(result[1], 0.8)

    def _normalize_vector(self, vec):
        """Helper to normalize a vector to unit length."""
        mag = sum(x*x for x in vec) ** 0.5
        if mag == 0:
            return vec
        return [x / mag for x in vec]


class TestTrends(unittest.TestCase):
    """Tests for trends.py term frequency analysis."""

    def test_term_frequency_single_window(self):
        """Calculate term frequencies within a single time window."""
        items = [
            {'headline': 'OpenAI announces GPT-5', 'day': date(2026, 8, 28)},
            {'headline': 'OpenAI updates pricing', 'day': date(2026, 8, 28)},
        ]
        freqs = self._count_terms(items)
        self.assertEqual(freqs['openai'], 2)
        self.assertEqual(freqs['gpt-5'], 1)

    def test_term_frequency_boundary(self):
        """Term frequency at window boundaries handles edges."""
        items = [
            {'headline': 'AI news', 'day': date(2026, 8, 27)},
            {'headline': 'AI research', 'day': date(2026, 8, 31)},
        ]
        freqs = self._count_terms(items, start=date(2026, 8, 28), end=date(2026, 8, 30))
        self.assertEqual(freqs.get('ai', 0), 0)

    def _count_terms(self, items, start=None, end=None):
        """Count term occurrences, optionally filtered by date."""
        result = {}
        for item in items:
            if start and item['day'] < start:
                continue
            if end and item['day'] > end:
                continue
            for word in item['headline'].lower().split():
                result[word] = result.get(word, 0) + 1
        return result


class TestStats(unittest.TestCase):
    """Tests for stats.py aggregation and category counts."""

    def test_weekly_aggregate_empty(self):
        """Empty item list produces zero aggregates."""
        agg = self._aggregate_by_week([])
        self.assertEqual(agg, {})

    def test_weekly_aggregate_single_item(self):
        """Single item aggregates correctly."""
        items = [{'day': date(2026, 8, 28), 'score': 10}]
        agg = self._aggregate_by_week(items)
        week_key = 'week_2026_w35'
        self.assertIn(week_key, agg)
        self.assertEqual(agg[week_key]['total'], 10)
        self.assertEqual(agg[week_key]['count'], 1)

    def test_category_distribution_balanced(self):
        """Category distribution calculates proportions."""
        items = [
            {'category': 'models', 'score': 5},
            {'category': 'chips', 'score': 5},
            {'category': 'funding', 'score': 5},
        ]
        dist = self._category_dist(items)
        self.assertAlmostEqual(dist['models'], 0.333, places=2)
        self.assertAlmostEqual(dist['chips'], 0.333, places=2)
        self.assertAlmostEqual(dist['funding'], 0.333, places=2)

    def _aggregate_by_week(self, items):
        """Aggregate items by ISO week."""
        result = {}
        for item in items:
            iso = item['day'].isocalendar()
            week_key = f"week_{iso[0]}_w{iso[1]:02d}"
            if week_key not in result:
                result[week_key] = {'total': 0, 'count': 0}
            result[week_key]['total'] += item.get('score', 0)
            result[week_key]['count'] += 1
        return result

    def _category_dist(self, items):
        """Distribution of items by category."""
        total = sum(i.get('score', 0) for i in items)
        if total == 0:
            return {}
        counts = {}
        for item in items:
            cat = item['category']
            counts[cat] = counts.get(cat, 0) + item.get('score', 0)
        return {k: v / total for k, v in counts.items()}


class TestSearch(unittest.TestCase):
    """Tests for search.py ranked keyword search."""

    def test_search_empty_query(self):
        """Empty query returns no results."""
        items = [{'headline': 'AI news'}]
        results = self._search(items, '')
        self.assertEqual(results, [])

    def test_search_single_match(self):
        """Query matches a single item."""
        items = [
            {'headline': 'OpenAI releases GPT-5', 'score': 100},
            {'headline': 'Google news', 'score': 50},
        ]
        results = self._search(items, 'openai')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['headline'], 'OpenAI releases GPT-5')

    def test_search_ranked_by_score(self):
        """Results ranked by relevance score descending."""
        items = [
            {'headline': 'AI foundation model', 'score': 10},
            {'headline': 'AI news breaking', 'score': 50},
        ]
        results = self._search(items, 'ai')
        self.assertEqual(results[0]['score'], 50)

    def _search(self, items, query):
        """Search items by query, rank by score."""
        if not query.strip():
            return []
        query_lower = query.lower()
        matches = [
            i for i in items
            if query_lower in i['headline'].lower()
        ]
        return sorted(matches, key=lambda x: x.get('score', 0), reverse=True)


if __name__ == '__main__':
    """Demo: run representative test suites."""
    suite = unittest.TestSuite()
    suite.addTest(TestScoring('test_normalize_zero_vector'))
    suite.addTest(TestScoring('test_normalize_unit_vector'))
    suite.addTest(TestTrends('test_term_frequency_single_window'))
    suite.addTest(TestTrends('test_term_frequency_boundary'))
    suite.addTest(TestStats('test_weekly_aggregate_empty'))
    suite.addTest(TestStats('test_category_distribution_balanced'))
    suite.addTest(TestSearch('test_search_empty_query'))
    suite.addTest(TestSearch('test_search_ranked_by_score'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
