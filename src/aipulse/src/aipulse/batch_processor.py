"""Batch processing utilities for AI Pulse digest items.

Provides efficient batch operations (tagging, scoring, filtering, transforming)
for large collections of news items with progress tracking and chunking support.
"""

from typing import Callable, List, Any, Dict, Optional, TypeVar
from dataclasses import dataclass
from models import NewsItem, Digest

T = TypeVar('T')


@dataclass
class BatchConfig:
    chunk_size: int = 100
    track_progress: bool = False
    on_chunk_done: Optional[Callable[[int], None]] = None


def chunk_items(items: List[T], size: int) -> List[List[T]]:
    """Split items into fixed-size chunks."""
    chunks = []
    for i in range(0, len(items), size):
        chunks.append(items[i:i+size])
    return chunks


def batch_map(items: List[T], func: Callable[[T], Any],
             config: Optional[BatchConfig] = None) -> List[Any]:
    """Apply function to items in batches."""
    if config is None:
        config = BatchConfig()
    results = []
    chunks = chunk_items(items, config.chunk_size)
    for chunk in chunks:
        for item in chunk:
            results.append(func(item))
        if config.on_chunk_done:
            config.on_chunk_done(len(chunks))
    return results


def batch_filter(items: List[NewsItem], predicate: Callable[[NewsItem], bool],
                config: Optional[BatchConfig] = None) -> List[NewsItem]:
    """Filter items matching predicate in batches."""
    if config is None:
        config = BatchConfig()
    results = []
    chunks = chunk_items(items, config.chunk_size)
    for chunk in chunks:
        for item in chunk:
            if predicate(item):
                results.append(item)
        if config.on_chunk_done:
            config.on_chunk_done(len(chunks))
    return results


def batch_tag(items: List[NewsItem], tagger_func: Callable[[NewsItem], List[str]],
             config: Optional[BatchConfig] = None) -> List[NewsItem]:
    """Batch tag items using provided tagger function."""
    if config is None:
        config = BatchConfig()
    tagged = []
    chunks = chunk_items(items, config.chunk_size)
    for chunk in chunks:
        for item in chunk:
            tags = tagger_func(item)
            item.entities.extend(tags)
            tagged.append(item)
        if config.on_chunk_done:
            config.on_chunk_done(len(chunks))
    return tagged


def batch_transform(items: List[NewsItem],
                   transform: Callable[[NewsItem], NewsItem],
                   config: Optional[BatchConfig] = None) -> List[NewsItem]:
    """Apply transformation to items in batches."""
    if config is None:
        config = BatchConfig()
    results = []
    chunks = chunk_items(items, config.chunk_size)
    for chunk in chunks:
        for item in chunk:
            results.append(transform(item))
        if config.on_chunk_done:
            config.on_chunk_done(len(chunks))
    return results


if __name__ == '__main__':
    from datetime import date
    digest = Digest(day=date(2026, 9, 10))
    digest.add(NewsItem('OpenAI GPT-6 Astra', 'New frontier model released', 'news', ''))
    digest.add(NewsItem('NVIDIA Vera Rubin', 'AI chip platform update', 'chips', ''))
    digest.add(NewsItem('AI Funding Boom', '7 models, huge checks for frontier', 'funding', ''))

    items = digest.items
    print(f'Processing {len(items)} items in batches...')
    tagger = lambda x: ['ai', 'tech']
    tagged = batch_tag(items, tagger, BatchConfig(chunk_size=2))
    print(f'Tagged {len(tagged)} items')
    filtered = batch_filter(tagged, lambda x: len(x.summary) > 10)
    print(f'Filtered to {len(filtered)} items with long summaries')
