"""Export: CSV and JSON exporters for AI digest archive.

Provides functions to export digests in standard formats
for sharing and external analysis.
"""

import csv
import json
from pathlib import Path


def export_to_csv(digests, output_file="digests_export.csv"):
    """Export digest items to CSV format.

    Args:
        digests: List of digest tuples (date, items) where items
                 are dicts with headline, summary, source, url.
        output_file: Output CSV file path.

    Returns:
        Path to created file.
    """
    rows = []
    for date, items in digests:
        for item in items:
            rows.append({
                'date': date,
                'headline': item.get('headline', ''),
                'summary': item.get('summary', ''),
                'source': item.get('source', ''),
                'url': item.get('url', '')
            })
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'headline', 'summary', 'source', 'url'])
        writer.writeheader()
        writer.writerows(rows)
    return output_file


def export_to_json(digests, output_file="digests_export.json"):
    """Export digest items to JSON format.

    Args:
        digests: List of digest tuples (date, items).
        output_file: Output JSON file path.

    Returns:
        Path to created file.
    """
    data = []
    for date, items in digests:
        data.append({'date': date, 'items': items})
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_file


if __name__ == "__main__":
    sample_digests = [
        ('2026-08-20', [
            {'headline': 'xAI expands Memphis GPU cluster', 'summary': 'Hundreds of thousands of GPUs.', 'source': 'News', 'url': ''},
            {'headline': 'EU AI Act enters force', 'summary': 'Full enforcement on August 2.', 'source': 'Regulation', 'url': ''}
        ])
    ]
    csv_file = export_to_csv(sample_digests)
    json_file = export_to_json(sample_digests)
    csv_size = Path(csv_file).stat().st_size
    json_size = Path(json_file).stat().st_size
    print(f"CSV export: {csv_file} ({csv_size} bytes)")
    print(f"JSON export: {json_file} ({json_size} bytes)")
