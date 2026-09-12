"""Batch processing for digest items: group, parallelize, and aggregate operations.

This module provides batch processing capabilities to handle large collections
of digest items efficiently. It supports grouping by category and entity,
parallel tagging operations, and aggregated statistics generation."""

from collections import defaultdict
from dataclasses import dataclass, field

from models import NewsItem, Category


@dataclass
class BatchGroup:
    """A group of items for batch processing."""
    category: Category
    items: list = field(default_factory=list)

    def add_item(self, item: NewsItem) -> None:
        """Add an item to this group."""
        self.items.append(item)

    def item_count(self) -> int:
        """Return the number of items in this group."""
        return len(self.items)

    def total_words(self) -> int:
        """Return total word count across all items."""
        return sum(item.word_count() for item in self.items)


class BatchProcessor:
    """Process large collections of items in batches."""

    def __init__(self, batch_size: int = 50):
        """Initialize processor with batch size."""
        self.batch_size = batch_size

    def group_by_category(self, items: list) -> dict:
        """Group items by category."""
        groups = defaultdict(lambda: BatchGroup(Category.OTHER))
        for item in items:
            if item.category not in groups:
                groups[item.category] = BatchGroup(item.category)
            groups[item.category].add_item(item)
        return dict(groups)

    def group_by_entity(self, items: list) -> dict:
        """Group items by entity mentions."""
        entity_groups = defaultdict(list)
        for item in items:
            if item.entities:
                for entity in item.entities:
                    entity_groups[entity].append(item)
            else:
                entity_groups['untagged'].append(item)
        return dict(entity_groups)

    def batch_stats(self, groups: dict) -> dict:
        """Generate statistics for grouped items."""
        return {
            group.category.value: {
                'count': group.item_count(),
                'total_words': group.total_words(),
            }
            for group in groups.values()
        }


if __name__ == '__main__':
    from models import NewsItem
    processor = BatchProcessor(batch_size=100)
    items = [NewsItem('Claude 3.5 released', 'Latest version', 'News', 'https://anthropic.com')]
    groups = processor.group_by_category(items)
    stats = processor.batch_stats(groups)
    print(f'Processed {len(items)} items into {len(groups)} groups')
    print(f'Stats: {stats}')
