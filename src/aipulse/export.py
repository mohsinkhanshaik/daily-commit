"""Export AI Pulse data to CSV and JSON formats.

This module provides interoperable exporters for digests and news items.
CSV rows preserve tabular structure (headers, escaping); JSON nests
hierarchies and preserves enums and lists. Both support field selection.
"""

import csv
import json
from dataclasses import asdict
from io import StringIO
from typing import Any, Optional

def to_csv(items: list[dict[str, Any]], fields: Optional[list[str]] = None) -> str:
    """Serialize items to CSV with proper escaping."""
    if not items:
        return ""

    if fields is None:
        fields = list(items[0].keys())

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()

    for item in items:
        # Convert enums to strings, lists to JSON strings
        row = {}
        for field in fields:
            val = item.get(field)
            if val is None:
                row[field] = ""
            elif isinstance(val, list):
                row[field] = json.dumps(val)
            else:
                row[field] = str(val)
        writer.writerow(row)

    return output.getvalue()


def to_json(items: list, fields: Optional[list[str]] = None, pretty: bool = True) -> str:
    """Serialize items to JSON preserving nested structure."""
    if fields:
        # Trim to selected fields only
        trimmed = []
        for item in items:
            if hasattr(item, '__dataclass_fields__'):
                d = asdict(item)
            else:
                d = item if isinstance(item, dict) else asdict(item)
            trimmed.append({k: d[k] for k in fields if k in d})
        data = trimmed
    else:
        # Keep full structure, convert dataclasses
        data = []
        for item in items:
            if hasattr(item, '__dataclass_fields__'):
                data.append(asdict(item))
            else:
                data.append(item if isinstance(item, dict) else asdict(item))

    indent = 2 if pretty else None
    return json.dumps(data, indent=indent, default=str)


if __name__ == "__main__":
    # Demo: export sample digest
    sample = [
        {"headline": "OpenAI pricing cut 80%", "category": "products", "entities": ["OpenAI"], "source": "blog"},
        {"headline": "Blackwell Ultra ramps", "category": "chips", "entities": ["NVIDIA"], "source": "news"}
    ]

    print("CSV Export:")
    print(to_csv(sample, fields=["headline", "category", "entities"]))
    print("\nJSON Export:")
    print(to_json(sample, pretty=True))
