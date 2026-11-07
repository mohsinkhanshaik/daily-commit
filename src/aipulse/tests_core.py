"""Regression tests for the core pipeline: models, parser, validate, tagger,
entities, archive, render, cache.

The previous tests_core.py could not run (it imported a function that never
existed, parse_digest_markdown) and its assertions were written so that
any result passed ("category in [MODELS, OTHER]"). These tests pin the
behavior fixed in the repair PR and fail loudly if it regresses.

Run all suites:  python -m unittest discover -s src/aipulse -p "tests_*.py"
"""

import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from archive import DigestArchive
from cache import Cache, cached_archive
from digest_parser import parse_digest
from entities import extract_entities
from models import Category, Digest, NewsItem
from render import render_digest
from tagger import tag_item
from validate import validate_format

SAMPLE = """# AI Pulse - 2026-08-29
Daily AI industry digest.
## Nvidia ships Rubin GPUs to data centers
Nvidia began volume shipments. Why it matters: compute supply loosens.
    Source: Reuters (https://reuters.com/a)
## OpenAI raises 40 billion dollars
The round values OpenAI at 300 billion. Why it matters: capital concentrates. Source: CNBC (https://cnbc.com/b), Bloomberg (https://bloomberg.com/c)
## Trend watch
Compute and capital keep clustering.
"""


class ModelTests(unittest.TestCase):
    def test_defaults_and_grouping(self):
        d = Digest(date(2026, 8, 29))
        d.add(NewsItem("a", "one two"))
        d.add(NewsItem("b", "x", category=Category.CHIPS))
        self.assertEqual(d.items[0].source, "")
        self.assertEqual(len(d.by_category(Category.CHIPS)), 1)
        self.assertEqual(set(d.by_category()), {Category.OTHER, Category.CHIPS})
        self.assertEqual(Digest(date(2026, 1, 1)).by_category(), {})
        self.assertIs(Category.parse("Chip"), Category.CHIPS)


class ParserTests(unittest.TestCase):
    def test_parses_sources_urls_and_trend(self):
        d = parse_digest(SAMPLE)
        self.assertEqual(d.day, date(2026, 8, 29))
        self.assertEqual(len(d), 2)
        self.assertEqual(d.items[0].url, "https://reuters.com/a")
        self.assertEqual(d.items[1].source, "CNBC")
        self.assertNotIn("Source:", d.items[1].summary)
        self.assertEqual(d.trend_watch, "Compute and capital keep clustering.")
        self.assertEqual(d.intro, "Daily AI industry digest.")

    def test_missing_day_raises_and_fallback_works(self):
        with self.assertRaises(ValueError):
            parse_digest("## x\ny")
        self.assertEqual(parse_digest("Intro\n## x\ny", "2026-01-02").day, date(2026, 1, 2))

    def test_render_round_trip(self):
        d = parse_digest(SAMPLE)
        again = parse_digest(render_digest(d))
        self.assertEqual([(i.headline, i.summary, i.url) for i in d.items],
                         [(i.headline, i.summary, i.url) for i in again.items])
        self.assertEqual(again.trend_watch, d.trend_watch)


class ValidateTests(unittest.TestCase):
    def test_trend_heading_is_warning_not_error(self):
        found = validate_format(SAMPLE, "2026-08-29.md")
        errors = [m for lvl, m in found if lvl == "ERROR"]
        self.assertEqual(errors, ["2 news sections, expected 5-7"])
        self.assertTrue(any("heading" in m for lvl, m in found if lvl == "WARN"))

    def test_filename_mismatch(self):
        found = validate_format(SAMPLE, "2026-08-30.md")
        self.assertTrue(any("does not match filename" in m for _, m in found))


class TaggerEntityTests(unittest.TestCase):
    def test_tagger_categories(self):
        self.assertIs(tag_item(NewsItem("Anthropic raises $1B", "Series B funding round")), Category.FUNDING)
        self.assertIs(tag_item(NewsItem("Nvidia GPU shortage", "Chip supply tight")), Category.CHIPS)
        self.assertIs(tag_item(NewsItem("Urban planners ruled", "Bank opened")), Category.OTHER)

    def test_entities_longest_match_and_names(self):
        e = extract_entities("OpenAI shipped GPT-5.6 while taken together the metadata grew; Kimi K3 too.")
        self.assertEqual(e.models, ["GPT-5.6", "Kimi K3"])
        self.assertEqual(e.companies, ["OpenAI", "Moonshot AI"])


class ArchiveCacheTests(unittest.TestCase):
    def test_archive_skips_dirs_and_records_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "2026-08-29.md").write_text(SAMPLE)
            Path(tmp, "2026-08-30.md").write_text("   ")
            Path(tmp, "2026-11-01.md").mkdir()
            arch = DigestArchive.load(tmp)
            self.assertEqual(arch.days(), ["2026-08-29"])
            self.assertEqual(len(arch.errors), 1)
            self.assertEqual(arch.digests["2026-08-29"].items[0].category, Category.CHIPS)
            self.assertEqual(arch.build_index()["total_items"], 2)

    def test_cache_ttl_zero_and_cached_none(self):
        c = Cache()
        c.set("none", None)
        c.set("zero", 1, ttl=0)
        self.assertIsNone(c.get("none", "MISS"))
        self.assertEqual(c.get("zero", "MISS"), "MISS")

    def test_cached_archive_invalidates_on_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "2026-08-29.md").write_text(SAMPLE)
            first = cached_archive(tmp)
            self.assertIs(first, cached_archive(tmp))
            Path(tmp, "2026-08-30.md").write_text(SAMPLE.replace("08-29", "08-30"))
            self.assertEqual(len(cached_archive(tmp).digests), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
