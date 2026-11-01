"""LLM-powered digest summaries via prompt-based generation.

This module provides functions to generate concise summaries of digest items
using a simple prompt template. It abstracts away the LLM call mechanism and
provides a configurable interface for different summary styles and lengths.
"""

from dataclasses import dataclass
from typing import Optional
from models import NewsItem, Digest


@dataclass
class SummaryConfig:
    """Configuration for summary generation."""
    style: str = 'concise'  # 'concise', 'technical', 'narrative'
    max_length: int = 100   # words
    include_entities: bool = True


def build_prompt(item: NewsItem, config: SummaryConfig) -> str:
    """Build a prompt for summarizing a news item."""
    style_hint = f"Style: {config.style} ({config.max_length} words max)."
    entity_hint = " Include key entities." if config.include_entities else ""
    return f"Summarize:\n{item.headline}\n{item.summary}\n\n{style_hint}{entity_hint}"


def mock_llm_call(prompt: str) -> str:
    """Mock LLM call for demonstration (returns placeholder).

    In production, this would call an actual LLM API (OpenAI, Anthropic, etc).
    """
    return "[LLM-generated summary placeholder]"


def summarize_item(item: NewsItem, config: Optional[SummaryConfig] = None) -> str:
    """Generate a summary for a single news item."""
    if config is None:
        config = SummaryConfig()
    prompt = build_prompt(item, config)
    return mock_llm_call(prompt)


def summarize_digest(digest: Digest, config: Optional[SummaryConfig] = None) -> dict:
    """Generate summaries for all items in a digest."""
    if config is None:
        config = SummaryConfig()
    return {
        item.headline: summarize_item(item, config)
        for item in digest.items
    }


if __name__ == "__main__":
    from models import Category
    item = NewsItem(
        headline="Test: LLM Summaries Ready",
        summary="LLM summary generation module initialized.",
        source="AI Pulse",
        category=Category.RESEARCH
    )
    config = SummaryConfig(style='concise', max_length=50)
    result = summarize_item(item, config)
    print(f"Item: {item.headline}")
    print(f"Summary: {result}")
