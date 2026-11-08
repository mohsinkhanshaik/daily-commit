"""Regression tests for the analysis layer: scoring, stats, trends, search,
sentiment, co-occurrence, impact, QA, aggregation, watchlist, compare,
summarize, CLI, feeds and performance.

The previous tests_analysis.py could not import (build_archive did not
exist, and tagger.py itself failed to import), used lowercase enum members
that raise AttributeError, and re-implemented the logic under test inline
instead of calling the modules, so even a passing run proved nothing.

Run all suites:  python -m unittest discover -s src/aipulse -p "tests_*.py"
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cli
from aggregator import Aggregator
from archive import DigestArchive
from compare import compare
from cooccur import analyze_cooccurrences
from feeds import parse_feed_text
from impact_metrics import impact_window
from models import Category, Digest, NewsItem
from performance import MetricsSeries, MetricType
from scoring import score
from search import Query, search
from semantic_qa import SemanticQA
from sentiment import Sentiment, score_item
from stats import week_key, weekly_summary
from summarize import extract_top_k
from trends import term_frequency
from watchlist import Watchlist


def item(head, body="", cat=Category.OTHER, **kw):
    return NewsItem(head, body, category=cat, **kw)


class ScoringStatsTests(unittest.TestCase):
    def test_score_range_and_recency(self):
        rich = item("x", "w " * 80, Category.RESEARCH, source="S", url="https://a.b",
                    entities=["A", "B", "C", "D"])
        self.assertEqual(score(rich), 10.0)
        self.assertLess(score(rich, date(2026, 1, 1), date(2026, 3, 1)), 10.0)
        self.assertGreaterEqual(score(item("", "")), 0.0)

    def test_iso_week_across_new_year(self):
        self.assertEqual(week_key(date(2027, 1, 1)), "2026-W53")
        weeks = weekly_summary([Digest(date(2026, 12, 31), [item("a")]),
                                Digest(date(2027, 1, 1), [item("b")])])
        self.assertEqual(list(weeks), ["2026-W53"])
        self.assertEqual(weeks["2026-W53"].item_count, 2)

    def test_p95_nearest_rank(self):
        series = MetricsSeries("m", list(MetricType)[0])
        for v in range(1, 21):
            series.add(float(v))
        self.assertEqual(series.p95(), 19.0)


class TextAnalysisTests(unittest.TestCase):
    def test_trends_drop_stopwords(self):
        tf = term_frequency([item("Nvidia ships", "The chips matter. Why it matters: the chips."),
                             item("Nvidia again", "and the chips")])
        self.assertEqual(tf, {"nvidia": 2, "chips": 2})

    def test_search_whole_words(self):
        d = Digest(date(2026, 8, 1), [item("Analysts said supply chain eased"), item("AI funding surge")])
        hits = search([d], Query("ai"))
        self.assertEqual([r.item.headline for r in hits], ["AI funding surge"])

    def test_sentiment_negation_and_substrings(self):
        self.assertIs(score_item(item("Urban bank opens window")), Sentiment.NEUTRAL)
        self.assertIs(score_item(item("Result is not a breakthrough")), Sentiment.NEGATIVE)
        self.assertIs(score_item(item("Chip stocks surged to a record")), Sentiment.POSITIVE)

    def test_qa_no_crash_on_ties_and_no_false_answers(self):
        qa = SemanticQA()
        qa.add_item("2026-01-01", "Same", "same text", "u1")
        qa.add_item("2026-01-02", "Same", "same text", "u2")
        self.assertEqual(len(qa.search("same")), 2)
        self.assertEqual(qa.answer("World Cup winner?").sources, [])


class EntityAnalysisTests(unittest.TestCase):
    def test_cooccurrence_returns_ranked_pairs(self):
        d = Digest(date(2026, 8, 1), [item("x", entities=["OpenAI", "Nvidia", "OpenAI"]),
                                      item("y", entities=["Nvidia", "OpenAI"])])
        pairs = analyze_cooccurrences([d])
        self.assertEqual([(p.entity_a, p.entity_b, p.count) for p in pairs], [("Nvidia", "OpenAI", 2)])

    def test_impact_trend_is_computed(self):
        data = {"2026-11-01": ["A"], "2026-11-02": ["A"], "2026-11-03": ["B"], "2026-11-04": ["B", "B"]}
        trends = {e.entity: e.trend for e in impact_window(data, "2026-11-01", "2026-11-04")}
        self.assertEqual(trends, {"A": "falling", "B": "new"})

    def test_watchlist_case_and_prefix(self):
        wl = Watchlist({"NVIDIA"}, {"GPT-6"})
        self.assertEqual(wl.matches(item("Nvidia and OpenAI", "GPT-6 Cyber is gated")), ["GPT-6", "NVIDIA"])
        self.assertEqual(Watchlist.from_json(wl.export_json()), wl)


class PipelineTests(unittest.TestCase):
    def test_aggregator_window_and_dedupe(self):
        agg = Aggregator()
        agg.add_source("a", Digest(date(2026, 11, 5), [item("DOJ launches AI task force", "Unit formed")]))
        agg.add_source("b", Digest(date(2026, 11, 6), [item("DOJ launches AI task force unit", "Unit formed")]))
        self.assertEqual(len(agg.by_date_range("2026-11-06", "2026-11-06").rows), 1)
        self.assertEqual(len(agg.dedupe_headlines().rows), 1)

    def test_compare_uses_real_data(self):
        arch = DigestArchive(digests={
            "2026-01-01": Digest(date(2026, 1, 1), [item("a", cat=Category.CHIPS, entities=["Nvidia"])]),
            "2026-02-01": Digest(date(2026, 2, 1), [item("b", cat=Category.POLICY, entities=["DOJ"])])})
        res = compare(arch, ("2026-01-01", "2026-01-31"), ("2026-02-01", "2026-02-28"))
        self.assertEqual(res.category_shift, {"chips": -1, "policy": 1})
        self.assertEqual(res.newcomers, ["DOJ"])

    def test_summary_collapses_duplicates(self):
        d1 = Digest(date(2026, 11, 1), [item("OpenAI gates GPT-6 Cyber model", "Access limited to partners")])
        d2 = Digest(date(2026, 11, 2), [item("OpenAI gates GPT-6 Cyber model", "Access limited to partners now")])
        self.assertEqual(len(extract_top_k([(d1.day, d1), (d2.day, d2)], k=5)), 1)

    def test_feeds_rss_titles_and_atom_links(self):
        rss = "<rss><channel><item><title>T</title><link>https://x</link></item></channel></rss>"
        atom = ('<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>A</title>'
                '<link href="https://y"/></entry></feed>')
        self.assertEqual([(i.title, i.url) for i in parse_feed_text(rss) + parse_feed_text(atom)],
                         [("T", "https://x"), ("A", "https://y")])

    def test_cli_status_reads_real_archive(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["status", "--format", "json"])
        self.assertEqual(code, 0)
        self.assertNotIn('"days": 16', buf.getvalue())
        self.assertIn('"latest"', buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
