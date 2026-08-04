"""Extractive digest summarization module.

Combines multiple daily digests into a single summary digest that highlights
the most important news items by importance score. Demonstrates multi-file
analysis using outputs from archive (day 5) and scoring (day 7) modules.
"""

from datetime import date, timedelta
from pathlib import Path
from dataclasses import dataclass, field

try:
    from .models import Digest, NewsItem, Category
    from .digest_parser import parse_digest_file
    from .scoring import score_items
except ImportError:
    from models import Digest, NewsItem, Category
    from digest_parser import parse_digest_file
    from scoring import score_items


def load_digests(start_date, end_date, digest_dir='digests'):
    """Load all digests in a date range.

    Args:
        start_date: datetime.date for range start
        end_date: datetime.date for range end
        digest_dir: directory containing digest markdown files

    Returns: list of (date, Digest) tuples
    """
    digests = []
    current = start_date
    digest_path = Path(digest_dir)

    while current <= end_date:
        filename = digest_path / f'{current.isoformat()}.md'
        if filename.exists():
            try:
                digest = parse_digest_file(str(filename))
                digests.append((current, digest))
            except Exception:
                pass
        current += timedelta(days=1)

    return digests


def extract_top_k(digests, k=10):
    """Extract top K items by importance score across digests.

    Args:
        digests: list of (date, Digest) tuples from load_digests
        k: number of top items to extract

    Returns: list of (date, NewsItem, score) tuples sorted by score desc
    """
    scored_items = []

    for day, digest in digests:
        for item in digest.items:
            scores = score_items([item])
            if scores:
                item_score = scores[0]
                scored_items.append((day, item, item_score))

    scored_items.sort(key=lambda x: x[2], reverse=True)
    return scored_items[:k]


def generate_summary_digest(items_with_dates, summary_date):
    """Compose a summary digest from top items.

    Args:
        items_with_dates: list of (date, NewsItem, score) from extract_top_k
        summary_date: date string for summary digest header

    Returns: Digest object representing the summary
    """
    summary = Digest(day=summary_date)

    for day, item, score in items_with_dates:
        new_item = NewsItem(
            headline=item.headline,
            summary=item.summary,
            source=item.source,
            url=getattr(item, 'url', ''),
            category=getattr(item, 'category', Category.OTHER)
        )
        summary.add(new_item)

    return summary


def render_summary_markdown(summary, start_date, end_date):
    """Render summary digest as markdown.

    Args:
        summary: Digest object from generate_summary_digest
        start_date: start date string of range
        end_date: end date string of range

    Returns: markdown string
    """
    lines = [
        f'# AI Pulse - Summary {start_date} to {end_date}',
        '',
        f'Top stories from {len(summary)} days of coverage.',
        ''
    ]

    for item in summary.items:
        lines.append(f'## {item.headline}')
        lines.append('')
        lines.append(item.summary)
        lines.append('')
        lines.append(f'Source: {item.source}')
        lines.append('')

    return '\n'.join(lines)


if __name__ == '__main__':
    from datetime import date

    start = date(2026, 7, 29)
    end = date(2026, 8, 4)

    print(f'Loading digests from {start} to {end}...')
    digests = load_digests(start, end)
    print(f'Loaded {len(digests)} digests')

    print('Extracting top 5 stories by importance...')
    top_items = extract_top_k(digests, k=5)
    print(f'Found {len(top_items)} top items')

    if top_items:
        print('Generating summary digest...')
        summary = generate_summary_digest(top_items, date.today())
        print('Summary digest:')
        print(render_summary_markdown(summary, str(start), str(end)))
