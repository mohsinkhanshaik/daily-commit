"""Render analysis results and digests as Markdown reports.

The render module generates formatted Markdown output from Digest objects
and analysis results, enabling sharing, archival, and human-readable reports
of AI Pulse data. Supports customizable templates and multi-section layouts
with headers, tables, and inline formatting.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Dict, Optional

from aipulse.models import Digest, NewsItem, Category


def digest_to_markdown(digest: Digest, title: Optional[str] = None) -> str:
    """Convert a Digest to a formatted Markdown report."""
    lines = []
    if title:
        lines.append(f"# {title}")
    lines.append(f"# AI Pulse - {digest.day.isoformat()}")
    lines.append("")
    lines.append(f"**Report generated:** {digest.day.isoformat()}")
    lines.append(f"**Total items:** {len(digest)}")
    lines.append("")
    lines.append("## By Category")
    by_cat = digest.by_category()
    for cat in sorted(by_cat.keys()):
        lines.append(f"### {cat.value.title()}")
        for item in by_cat[cat]:
            lines.append(f"- **{item.headline}** ({item.category.value})")
            lines.append(f"  {item.summary}")
            if item.source:
                lines.append(f"  *Source: {item.source}*")
            lines.append("")
    return "\n".join(lines)


def item_to_table_row(item: NewsItem) -> str:
    """Format a single NewsItem as a Markdown table row."""
    entities_str = ", ".join(item.entities) if item.entities else "None"
    return f"| {item.headline[:40]} | {item.category.value} | {entities_str[:30]} |"


def digest_to_table(digest: Digest) -> str:
    """Render digest items as a Markdown table."""
    lines = ["| Headline | Category | Entities |",
             "| --- | --- | --- |"]
    for item in digest.items:
        lines.append(item_to_table_row(item))
    return "\n".join(lines)


if __name__ == "__main__":
    from datetime import date
    from aipulse.models import Category, NewsItem, Digest

    digest = Digest(day=date.today())
    digest.add(NewsItem(
        headline="Test Article",
        summary="A sample summary for testing.",
        source="Test Source",
        category=Category.RESEARCH
    ))

    md = digest_to_markdown(digest, "Test Report")
    print(md)
    print("\n" + "="*50)
    print(digest_to_table(digest))
