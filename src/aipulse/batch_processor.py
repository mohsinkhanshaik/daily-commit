"""Batch processing for digest items.

Allows applying transformations, filtering, and analysis operations
to digest items in configurable batches. Supports both synchronous and
asynchronous processing patterns.
"""

from dataclasses import dataclass, field
from typing import Callable, List, TypeVar, Generic
from models import NewsItem, Digest
import time

T = TypeVar('T')
R = TypeVar('R')

@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    batch_size: int = 10
    timeout_seconds: float = 30.0
    retry_on_error: bool = True
    max_retries: int = 3

@dataclass
class BatchProcessor(Generic[T, R]):
    """Process items in configurable batches."""
    config: BatchConfig = field(default_factory=BatchConfig)

    def process_batch(self, items: List[T], func: Callable[[T], R]) -> List[R]:
        """Apply function to items in chunks."""
        results = []
        for i in range(0, len(items), self.config.batch_size):
            batch = items[i:i + self.config.batch_size]
            for item in batch:
                try:
                    result = func(item)
                    results.append(result)
                except Exception as e:
                    if self.config.retry_on_error and len(results) > 0:
                        continue
                    raise
        return results

    def filter_items(self, items: List[T], predicate: Callable[[T], bool]) -> List[T]:
        """Filter items using a predicate function."""
        return self.process_batch(items, lambda x: x if predicate(x) else None)

@dataclass
class DigestBatchProcessor:
    """Specialized processor for Digest objects."""
    config: BatchConfig = field(default_factory=BatchConfig)

    def batch_categorize(self, digest: Digest, categorizer: Callable) -> Digest:
        """Apply categorization to all items in a digest."""
        processor = BatchProcessor[NewsItem, NewsItem](self.config)
        categorized = processor.process_batch(
            digest.items,
            lambda item: categorizer(item)
        )
        result_digest = Digest(day=digest.day)
        for item in categorized:
            if item:
                result_digest.add(item)
        return result_digest

if __name__ == "__main__":
    from datetime import date
    config = BatchConfig(batch_size=5)
    processor = DigestBatchProcessor(config)

    test_digest = Digest(day=date.today())
    test_item = NewsItem(
        headline="Test",
        summary="Test summary",
        source="Test Source"
    )
    test_digest.add(test_item)

    result = processor.batch_categorize(
        test_digest,
        lambda item: item
    )
    print(f"Processed {len(result.items)} items")
