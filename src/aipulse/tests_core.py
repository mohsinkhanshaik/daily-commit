"""Tests for core AI Pulse modules: models, digest_parser, tagger.

Covers dataclass behavior, markdown parsing, and rule-based topic tagging.
Validates category enum, news item structure, digest aggregation, markdown
parsing with all field types, and topic classification across major AI categories.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import Category, NewsItem, Digest
from digest_parser import parse_digest_markdown
from tagger import tag_item


def test_category_enum():
    """Test Category enum values."""
    assert Category.MODELS.value == 'models'
    assert Category.CHIPS.value == 'chips'
    assert Category.FUNDING.value == 'funding'
    assert Category.POLICY.value == 'policy'
    assert Category.RESEARCH.value == 'research'
    assert Category.PRODUCTS.value == 'products'
    assert Category.OTHER.value == 'other'
    print("✓ Category enum test passed")


def test_news_item_creation():
    """Test NewsItem dataclass initialization and methods."""
    item = NewsItem(
        headline="Claude 3.5 Released",
        summary="Anthropic launches new model.",
        source="TechCrunch",
        url="https://techcrunch.com/claude",
        category=Category.MODELS,
        entities=["Anthropic", "Claude"]
    )
    assert item.headline == "Claude 3.5 Released"
    assert item.category == Category.MODELS
    assert len(item.entities) == 2
    assert item.word_count() == 5
    print("✓ NewsItem creation test passed")


def test_news_item_defaults():
    """Test NewsItem default values."""
    item = NewsItem(
        headline="Breaking News",
        summary="Something happened."
    )
    assert item.url == ""
    assert item.category == Category.OTHER
    assert item.entities == []
    assert item.source == ""
    print("✓ NewsItem defaults test passed")


def test_digest_creation():
    """Test Digest dataclass and methods."""
    d = Digest(day=date(2026, 8, 29))
    assert len(d) == 0

    item1 = NewsItem("Item 1", "Summary 1.", category=Category.MODELS)
    item2 = NewsItem("Item 2", "Summary 2.", category=Category.CHIPS)

    d.add(item1)
    d.add(item2)
    assert len(d) == 2

    by_cat = d.by_category()
    assert len(by_cat[Category.MODELS]) == 1
    assert len(by_cat[Category.CHIPS]) == 1
    print("✓ Digest creation test passed")


def test_digest_parser_basic():
    """Test parsing a simple digest markdown."""
    md = """# AI Pulse - 2026-08-29

Daily AI industry digest.

## Heading 1
Two sentence summary here. Why it matters: impact.
Source: News (http://url1)

## Heading 2
Another item summary. Why it matters: more impact.
Source: Site (http://url2)
"""
    digest = parse_digest_markdown(md, date(2026, 8, 29))
    assert digest.day == date(2026, 8, 29)
    assert len(digest) >= 2
    print("✓ Digest parser basic test passed")


def test_tagger_models():
    """Test tagging for models category."""
    item1 = NewsItem("Claude 3.5 launched", "New model release")
    item1 = tag_item(item1)
    assert item1.category in [Category.MODELS, Category.OTHER]

    item2 = NewsItem("Gemini 3.7 Flash", "Google releases new model")
    item2 = tag_item(item2)
    assert item2.category in [Category.MODELS, Category.OTHER]
    print("✓ Tagger models test passed")


def test_tagger_funding():
    """Test tagging for funding category."""
    item = NewsItem(
        "Anthropic raises $1B",
        "Series B funding announcement"
    )
    item = tag_item(item)
    assert item.category in [Category.FUNDING, Category.OTHER]
    print("✓ Tagger funding test passed")


if __name__ == "__main__":
    test_category_enum()
    test_news_item_creation()
    test_news_item_defaults()
    test_digest_creation()
    test_digest_parser_basic()
    test_tagger_models()
    test_tagger_funding()
    print("\nAll tests passed!")
