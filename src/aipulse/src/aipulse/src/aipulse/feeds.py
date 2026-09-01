"""
Multi-source digest integration for external API feeds (day 31).

Extends AI Pulse to ingest structured data from RSS, REST APIs, and JSONL
batches. FeedSource tracks external sources; FeedFetcher polls them; Digester
converts to canonical NewsItem format with stdlib-only parsing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from xml.etree import ElementTree as ET
from urllib.parse import urljoin
import json


class FeedType(Enum):
    RSS = "rss"
    ATOM = "atom"
    REST_JSON = "rest_json"
    JSONL = "jsonl"


@dataclass
class FeedSource:
    """External data source for news ingestion."""
    name: str
    url: str
    feed_type: FeedType
    last_checked: datetime = field(default_factory=datetime.now)
    active: bool = True
    description: str = ""


@dataclass
class FeedItem:
    """Raw item from a feed before conversion to NewsItem."""
    title: str
    url: str
    summary: str = ""
    source_name: str = ""
    published: datetime = field(default_factory=datetime.now)


class FeedFetcher:
    """Polls external feeds and extracts items."""

    def __init__(self, timeout: int = 10, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch_rss(self, url: str) -> List[FeedItem]:
        """Parse RSS/Atom feed and extract items."""
        items = []
        try:
            tree = ET.parse(url)
            root = tree.getroot()
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for item in root.findall(".//item") + root.findall("atom:entry", ns):
                title_elem = item.find("title") or item.find("atom:title", ns)
                link_elem = item.find("link") or item.find("atom:link[@rel='alternate']", ns)
                summary_elem = item.find("description") or item.find("atom:summary", ns)

                title = title_elem.text if title_elem is not None else "Untitled"
                url_val = link_elem.text if link_elem is not None else ""
                summary = summary_elem.text if summary_elem is not None else ""

                items.append(FeedItem(title=title, url=url_val, summary=summary))
        except Exception:
            pass
        return items

    def fetch_jsonl(self, path: str) -> List[FeedItem]:
        """Parse JSONL batch file with news items."""
        items = []
        try:
            with open(path, 'r') as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        items.append(FeedItem(
                            title=obj.get("title", ""),
                            url=obj.get("url", ""),
                            summary=obj.get("summary", "")
                        ))
        except Exception:
            pass
        return items


class Digester:
    """Convert feed items to canonical NewsItem format."""

    def digest(self, items: List[FeedItem], source: FeedSource) -> List[dict]:
        """Convert FeedItems to NewsItem-compatible dicts."""
        digested = []
        for item in items:
            digested.append({
                "headline": item.title,
                "summary": item.summary,
                "source": source.name,
                "url": item.url,
                "category": "other",
                "entities": [],
                "word_count": len(item.summary.split())
            })
        return digested


if __name__ == "__main__":
    fetcher = FeedFetcher()
    digester = Digester()

    source = FeedSource(
        name="Example RSS",
        url="http://example.com/feed.xml",
        feed_type=FeedType.RSS,
        description="Example feed for testing"
    )

    items = [
        FeedItem(
            title="AI Research Breakthrough",
            url="http://example.com/ai-news",
            summary="New model achieves state-of-art results",
            source_name="Example"
        )
    ]

    digested = digester.digest(items, source)
    print(f"Digested {len(digested)} items from {source.name}")
    for item in digested:
        print(f"  - {item['headline']}")
