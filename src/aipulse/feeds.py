"""External feed ingestion: RSS 2.0, Atom and JSONL into NewsItems.

This module was committed to the wrong path (src/aipulse/src/aipulse/src/
aipulse/feeds.py), so nothing could import it. Moving it exposed bugs that
made it return garbage even for valid feeds:

- `item.find("title") or item.find("atom:title")`: an ElementTree Element
  with no CHILDREN is falsy even when it has text, so the `or` always took
  the fallback. Every RSS title came back as "Untitled". Lookups now test
  `is not None` explicitly.
- Atom links live in the href ATTRIBUTE, not the element text, so Atom
  items had empty URLs. Atom also needs the namespace on every child tag.
- ET.parse(url) treats a URL as a local filename; fetching now goes
  through urllib with a timeout, and parsing (parse_feed_text) is separate
  so it can be tested offline.
- Every error was swallowed with `except Exception: pass`; errors are now
  returned to the caller alongside the items.
- The Digester produced loose dicts; to_news_items() builds real NewsItem
  objects, tagged and entity-annotated like archive items.
"""

import json
import urllib.request
from dataclasses import dataclass
from xml.etree import ElementTree as ET

from entities import annotate
from models import NewsItem
from tagger import tag_item

ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass
class FeedItem:
    title: str
    url: str
    summary: str = ""
    published: str = ""


def _text(node, *tags):
    for tag in tags:
        found = node.find(tag)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return ""


def parse_feed_text(xml_text):
    """FeedItems from RSS 2.0 or Atom XML text."""
    root = ET.fromstring(xml_text)
    items = []
    for node in root.iter("item"):
        items.append(FeedItem(_text(node, "title") or "Untitled", _text(node, "link"),
                              _text(node, "description"), _text(node, "pubDate")))
    for node in root.iter(ATOM + "entry"):
        link = ""
        for candidate in node.findall(ATOM + "link"):
            if candidate.get("rel", "alternate") == "alternate":
                link = candidate.get("href", "")
                break
        items.append(FeedItem(_text(node, ATOM + "title") or "Untitled", link,
                              _text(node, ATOM + "summary", ATOM + "content"),
                              _text(node, ATOM + "updated", ATOM + "published")))
    return items


def parse_jsonl_text(text):
    """FeedItems from JSON Lines; returns (items, errors)."""
    items, errors = [], []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            items.append(FeedItem(obj.get("title", ""), obj.get("url", ""),
                                  obj.get("summary", ""), obj.get("published", "")))
        except (ValueError, AttributeError) as exc:
            errors.append("line %d: %s" % (number, exc))
    return items, errors


def fetch_feed(url, timeout=10):
    """Download and parse a feed; returns (items, errors)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return parse_feed_text(resp.read()), []
    except (OSError, ET.ParseError, ValueError) as exc:
        return [], ["%s: %s" % (url, exc)]


def to_news_items(feed_items, source_name):
    """Tagged, entity-annotated NewsItems from FeedItems."""
    out = []
    for fi in feed_items:
        item = NewsItem(fi.title, fi.summary, source_name, fi.url)
        item.category = tag_item(item)
        out.append(annotate(item))
    return out


if __name__ == "__main__":
    rss = """<rss><channel><item><title>Nvidia ships Rubin GPUs</title>
    <link>https://example.com/rubin</link><description>Nvidia began shipping Rubin chips to data center customers.</description>
    </item></channel></rss>"""
    atom = """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>OpenAI raises 40 billion dollars</title>
    <link rel="alternate" href="https://example.com/oai"/><summary>OpenAI closed a funding round led by SoftBank.</summary>
    </entry></feed>"""
    for text in (rss, atom):
        for item in to_news_items(parse_feed_text(text), "demo"):
            print("%-34s %-8s %s %s" % (item.headline, item.category.value, item.url, item.entities))
