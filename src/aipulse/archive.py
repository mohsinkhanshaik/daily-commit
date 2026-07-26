"""Archive module - Load and index digest files.

Builds a queryable JSON-compatible archive of all digests in the digests/
folder, mapping dates to lists of parsed news items.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from digest_parser import parse_digest


def load_archive(digests_dir='digests'):
    """Load all digests from the digests/ folder into a dict.

    Args:
        digests_dir: Path to directory containing YYYY-MM-DD.md files.

    Returns:
        Dict mapping date strings to lists of parsed NewsItem objects.
    """
    archive = {}
    path = Path(digests_dir)

    if not path.exists():
        return archive

    for md_file in sorted(path.glob('*.md')):
        date_str = md_file.stem
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                items = parse_digest(content)
                archive[date_str] = items
        except Exception:
            pass

    return archive


def date_range_query(archive, start_date, end_date):
    """Filter archive items within a date range.

    Args:
        archive: Archive dict from load_archive().
        start_date: Start date string YYYY-MM-DD.
        end_date: End date string YYYY-MM-DD.

    Returns:
        Dict of dates within range and their items.
    """
    result = {}
    for date_str, items in archive.items():
        if start_date <= date_str <= end_date:
            result[date_str] = items
    return result


if __name__ == "__main__":
    archive = load_archive()
    print(f"Archive loaded: {len(archive)} days")
    for date_str in sorted(archive.keys()):
        count = len(archive[date_str])
        print(f"  {date_str}: {count} items")
