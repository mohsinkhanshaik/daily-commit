"""Render AI Pulse digests to markdown format.

This module provides functions to convert Digest model objects back to markdown,
enabling report generation and template-based rendering of AI industry analysis.
"""

from datetime import date
from aipulse.models import Digest


def render_digest(digest: Digest) -> str:
    """Render a Digest object to markdown string.

    Args:
        digest: A Digest model object with date and items.

    Returns:
        A markdown-formatted string representing the digest.
    """
    lines = [f"# AI Pulse - {digest.day.isoformat()}"]
    lines.append("")

    if not digest.items:
        lines.append("No items recorded for this date.")
        return "\n".join(lines)

    for item in digest.items:
        lines.append(f"## {item.headline}")
        lines.append("")
        lines.append(item.summary)
        lines.append("")
        if item.url:
            lines.append(f"Source: {item.source or 'Unknown'} ({item.url})")
        else:
            lines.append(f"Source: {item.source or 'Unknown'}")
        lines.append("")

    return "\n".join(lines)


def render_by_category(digest: Digest) -> dict:
    """Group and render digest items by category.

    Args:
        digest: Digest model object.

    Returns:
        Dict mapping category names to markdown strings.
    """
    result = {}
    categories = digest.by_category()
    for cat, items in categories.items():
        lines = [f"## {cat.value.title()}", ""]
        for item in items:
            lines.append(f"### {item.headline}")
            lines.append(item.summary)
            lines.append("")
        result[cat.value] = "\n".join(lines)
    return result


if __name__ == "__main__":
    from datetime import date
    from aipulse.models import Digest, NewsItem, Category

    digest = Digest(day=date.today())
    digest.add(NewsItem(
        headline="AI Model Pricing Down 80%",
        summary="Frontier labs cut costs dramatically. Why it matters: cheaper access drives adoption.",
        source="TechNews",
        url="https://example.com/1",
        category=Category.RESEARCH
    ))
    digest.add(NewsItem(
        headline="Chip Shortage Easing in Q3",
        summary="Supply constraints improving. Why it matters: infrastructure deployment accelerates.",
        source="SemiWatch",
        url="https://example.com/2",
        category=Category.CHIPS
    ))

    print(render_digest(digest))
