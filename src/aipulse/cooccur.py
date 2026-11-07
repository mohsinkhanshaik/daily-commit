"""Entity co-occurrence pairs across digests.

Two entities co-occur when the same news item mentions both. The ranked
pairs feed relationship maps ("who keeps appearing with Nvidia?").

The day-12 file was a SyntaxError: `return result` had drifted below the
__main__ block, so analyze_cooccurrences() fell off its end (returning
None) and Python rejected the module outright. Other bugs fixed here:

- The demo imported `src.aipulse.models`, a path that only works from one
  directory; it now uses the toolkit's flat imports like every module.
- Items with an empty `entities` list contributed nothing even though
  their text named companies. Entities are extracted when missing.
- Duplicate names inside one item ("OpenAI ... OpenAI") produced a
  self-pair (OpenAI, OpenAI); names are de-duplicated first.
- end_date was "last seen in iteration order", which is wrong when
  digests arrive unsorted; first/last seen now use min/max.
- Ties were broken by dict order; ranking is now (-count, a, b) so the
  output is deterministic.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date
from itertools import combinations


@dataclass
class CooccurrencePair:
    entity_a: str
    entity_b: str
    count: int
    start_date: date
    end_date: date


def _item_entities(item):
    if item.entities:
        return sorted(set(item.entities))
    from entities import extract_entities
    return sorted(set(extract_entities(item.headline + " " + item.summary).all()))


def analyze_cooccurrences(digest_list, min_threshold=1):
    """CooccurrencePair list sorted by count desc, then names."""
    counts = Counter()
    first, last = {}, {}
    for digest in digest_list:
        for item in digest.items:
            for pair in combinations(_item_entities(item), 2):
                counts[pair] += 1
                first[pair] = min(first.get(pair, digest.day), digest.day)
                last[pair] = max(last.get(pair, digest.day), digest.day)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [CooccurrencePair(a, b, n, first[(a, b)], last[(a, b)])
            for (a, b), n in ranked if n >= min_threshold]


def partners(pairs, entity):
    """Counter of entities that co-occur with `entity`."""
    out = Counter()
    for p in pairs:
        if entity in (p.entity_a, p.entity_b):
            out[p.entity_b if p.entity_a == entity else p.entity_a] += p.count
    return out


if __name__ == "__main__":
    from models import Digest, NewsItem
    d2 = Digest(date(2026, 8, 2), [NewsItem("OpenAI and Nvidia sign deal", "OpenAI buys GPUs.")])
    d1 = Digest(date(2026, 8, 1), [
        NewsItem("x", "", entities=["OpenAI", "Nvidia", "OpenAI"]),
        NewsItem("AMD courts OpenAI", "Nvidia rival AMD pitches OpenAI.")])
    pairs = analyze_cooccurrences([d2, d1])
    for p in pairs:
        print("%s <-> %s: %d (%s..%s)" % (p.entity_a, p.entity_b, p.count, p.start_date, p.end_date))
    print("Nvidia partners:", dict(partners(pairs, "Nvidia")))
