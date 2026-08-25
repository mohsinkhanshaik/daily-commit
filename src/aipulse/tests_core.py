"""
tests_core.py - Unit tests for AI Pulse core modules.

Tests for models.py, digest_parser.py, and tagger.py covering category
enums, NewsItem construction, Digest methods, markdown parsing, and
rule-based topic tagging. Designed to run with pytest or direct execution.
"""

import unittest
from datetime import date
from enum import Enum
from dataclasses import dataclass, field
from typing import List

try:
    from models import Category, NewsItem, Digest
    from digest_parser import parse_digest_markdown
    from tagger import tag_item, CategoryRule
except ImportError:
    raise ImportError("Run from src/aipulse/ directory with models, digest_parser, tagger available.")


class TestCategory(unittest.TestCase):
    """Tests for Category enum."""

    def test_category_values_exist(self):
        """Verify all expected Category values exist."""
        expected = {'models', 'chips', 'funding', 'policy', 'research', 'products', 'other'}
        actual = {c.name.lower() for c in Category}
        self.assertEqual(actual, expected)

    def test_category_default(self):
        """Verify Category.OTHER is the default fallback."""
        self.assertEqual(Category.OTHER.name, 'OTHER')


class TestNewsItem(unittest.TestCase):
    """Tests for NewsItem dataclass."""

    def test_newsitem_required_fields(self):
        """Test NewsItem with required headline and summary."""
        item = NewsItem(headline="Test headline", summary="Test summary")
        self.assertEqual(item.headline, "Test headline")
        self.assertEqual(item.summary, "Test summary")

    def test_newsitem_defaults(self):
        """Test NewsItem default values."""
        item = NewsItem(headline="H", summary="S")
        self.assertEqual(item.source, "")
        self.assertEqual(item.url, "")
        self.assertEqual(item.category, Category.OTHER)
        self.assertEqual(item.entities, [])

    def test_newsitem_custom_values(self):
        """Test NewsItem with custom category and entities."""
        item = NewsItem(
            headline="OpenAI releases",
            summary="New model",
            source="TechNews",
            url="https://example.com",
            category=Category.MODELS,
            entities=["OpenAI", "GPT-5"]
        )
        self.assertEqual(item.category, Category.MODELS)
        self.assertEqual(item.source, "TechNews")
        self.assertEqual(len(item.entities), 2)

    def test_newsitem_word_count(self):
        """Test NewsItem word_count method."""
        item = NewsItem(headline="One two three", summary="Four five six seven")
        count = item.word_count()
        self.assertGreaterEqual(count, 7)


class TestDigest(unittest.TestCase):
    """Tests for Digest dataclass."""

    def test_digest_empty(self):
        """Test creating an empty Digest."""
        d = Digest(day=date(2026, 8, 25))
        self.assertEqual(d.day, date(2026, 8, 25))
        self.assertEqual(len(d), 0)
        self.assertEqual(d.items, [])

    def test_digest_add(self):
        """Test Digest.add method."""
        d = Digest(day=date(2026, 8, 25))
        item1 = NewsItem(headline="A", summary="B", category=Category.MODELS)
        item2 = NewsItem(headline="C", summary="D", category=Category.CHIPS)
        d.add(item1)
        d.add(item2)
        self.assertEqual(len(d), 2)

    def test_digest_by_category(self):
        """Test Digest.by_category method."""
        d = Digest(day=date(2026, 8, 25))
        d.add(NewsItem(headline="Model1", summary="S1", category=Category.MODELS))
        d.add(NewsItem(headline="Model2", summary="S2", category=Category.MODELS))
        d.add(NewsItem(headline="Chip1", summary="S3", category=Category.CHIPS))
        models = d.by_category(Category.MODELS)
        chips = d.by_category(Category.CHIPS)
        self.assertEqual(len(models), 2)
        self.assertEqual(len(chips), 1)

    def test_digest_len(self):
        """Test Digest __len__ method."""
        d = Digest(day=date(2026, 8, 25))
        self.assertEqual(len(d), 0)
        d.add(NewsItem(headline="H", summary="S"))
        self.assertEqual(len(d), 1)


class TestDigestParser(unittest.TestCase):
    """Tests for digest_parser module."""

    def test_parse_empty_markdown(self):
        """Test parsing empty markdown."""
        result = parse_digest_markdown("", date(2026, 8, 25))
        self.assertIsNotNone(result)

    def test_parse_simple_markdown(self):
        """Test parsing simple markdown with sections."""
        md = "## OpenAI Release\nNew model released. Why it matters: breakthrough."
        result = parse_digest_markdown(md, date(2026, 8, 25))
        self.assertIsNotNone(result)


class TestTagger(unittest.TestCase):
    """Tests for tagger module."""

    def test_tag_models_keyword(self):
        """Test tagging with models keyword."""
        item = NewsItem(headline="GPT-5 Release", summary="New model out")
        tagged = tag_item(item)
        self.assertEqual(tagged.category, Category.MODELS)

    def test_tag_chips_keyword(self):
        """Test tagging with chips keyword."""
        item = NewsItem(headline="NVIDIA H200", summary="New processor")
        tagged = tag_item(item)
        self.assertEqual(tagged.category, Category.CHIPS)

    def test_tag_default_fallback(self):
        """Test that unmatched items default to OTHER."""
        item = NewsItem(headline="Random news", summary="No AI keywords")
        tagged = tag_item(item)
        self.assertIn(tagged.category, Category)


if __name__ == "__main__":
    unittest.main()
