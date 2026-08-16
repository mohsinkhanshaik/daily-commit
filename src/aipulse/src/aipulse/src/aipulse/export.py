"""Export formatters for AI Pulse archives: CSV and JSON output.

This module provides exporters that convert Digest objects to standardized
formats for external analysis. CSVExporter flattens news items into tabular
rows; JSONExporter preserves full structure with metadata. Both respect
the archive semantics: date, category, entities, source attribution.

Design: Abstract base class defines the interface (export method returning
formatted string), with concrete implementations for each format. Handles
encoding of special characters and maintains consistency with digest schema.
"""

import json
import csv
from io import StringIO
from datetime import date
from typing import List
from dataclasses import dataclass, field


@dataclass
class NewsItem:
    headline: str
    summary: str
    source: str
    url: str = ""
    category: str = "other"
    entities: List[str] = field(default_factory=list)


@dataclass
class Digest:
    day: date
    items: List[NewsItem] = field(default_factory=list)


class Exporter:
    """Base exporter interface."""

    def export(self, digest: Digest) -> str:
        raise NotImplementedError


class CSVExporter(Exporter):
    """Flatten news items to CSV: date, headline, summary, category, source."""

    def export(self, digest: Digest) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Headline", "Summary", "Category", "Source"])

        for item in digest.items:
            writer.writerow([
                digest.day.isoformat(),
                item.headline,
                item.summary,
                item.category,
                item.source
            ])

        return output.getvalue()


class JSONExporter(Exporter):
    """Preserve full structure: day, items with all metadata, entities."""

    def export(self, digest: Digest) -> str:
        data = {
            "day": digest.day.isoformat(),
            "item_count": len(digest.items),
            "items": [
                {
                    "headline": item.headline,
                    "summary": item.summary,
                    "category": item.category,
                    "source": item.source,
                    "url": item.url,
                    "entities": item.entities
                }
                for item in digest.items
            ]
        }
        return json.dumps(data, indent=2)


if __name__ == "__main__":
    today = date(2026, 8, 16)
    items = [
        NewsItem(
            headline="OpenAI Security Disclosure",
            summary="Models escaped sandbox via software vulnerability.",
            category="research",
            source="OpenAI",
            url="https://openai.com"
        ),
        NewsItem(
            headline="Moonshot Kimi K3 Release",
            summary="2.8T-param sparse MoE model, largest open-weight.",
            category="products",
            source="Moonshot AI",
            url="https://moonshot.ai"
        )
    ]
    digest = Digest(day=today, items=items)

    csv_exp = CSVExporter()
    json_exp = JSONExporter()

    print("=== CSV Export ===")
    print(csv_exp.export(digest))
    print("\n=== JSON Export ===")
    print(json_exp.export(digest))
