"""Multi-digest aggregation and cross-source analytics.

Aggregator merges digests from several named sources (our own digests, an
external feed, a partner newsletter) into one view that can be deduped and
windowed by date.

The day-35 module crashed at import with "cannot import name 'list' from
'typing'" (built-in generics are not exported by typing). Fixing that
exposed logic bugs that made every method except merged() wrong:

- by_date_range() compared the first four characters of each HEADLINE
  with the requested dates, so "2026-08-01".."2026-08-31" kept any story
  whose headline happened to sort between them. Merged rows now carry
  their digest's day and source, and the window filters on the real day.
- dedupe_headlines(min_sim) ignored min_sim and dropped only byte-identical
  headlines. It now uses dedupe.py's normalized word-set Jaccard, keeping
  the earliest report of each story and recording which sources repeated it.
- date_range was never filled in by merged(); it now spans the data.
- Merging lost provenance: AggregatedDigest.items held bare NewsItems, so
  "which source said this?" was unanswerable. Rows are (day, source, item).
"""

from dataclasses import dataclass, field

from dedupe import jaccard_similarity, normalize_text
from models import Digest


@dataclass
class AggregatedDigest:
    name: str
    rows: list = field(default_factory=list)          # (day, source, NewsItem)
    sources: set = field(default_factory=set)
    also_reported_by: dict = field(default_factory=dict)  # headline -> [source]

    @property
    def items(self):
        return [item for _, _, item in self.rows]

    @property
    def date_range(self):
        days = sorted(day for day, _, _ in self.rows)
        return (days[0].isoformat(), days[-1].isoformat()) if days else ("", "")

    @property
    def source_count(self):
        return len(self.sources)


class Aggregator:
    def __init__(self):
        self.feeds = {}  # source name -> [Digest]

    def add_source(self, name: str, digest: Digest) -> None:
        """Register one digest under a source name (call repeatedly per day)."""
        self.feeds.setdefault(name, []).append(digest)

    def merged(self, name: str = "merged") -> AggregatedDigest:
        agg = AggregatedDigest(name=name)
        for source, digests in self.feeds.items():
            for digest in digests:
                agg.sources.add(source)
                agg.rows += [(digest.day, source, item) for item in digest.items]
        agg.rows.sort(key=lambda row: (row[0], row[1]))
        return agg

    def dedupe_headlines(self, min_sim: float = 0.6) -> AggregatedDigest:
        """Merge, then drop stories whose text is >= min_sim similar to one kept."""
        agg = self.merged("deduped")
        kept, words = [], []
        for day, source, item in agg.rows:
            text = normalize_text(item.headline + " " + item.summary)
            match = next((k for k, w in zip(kept, words) if jaccard_similarity(text, w) >= min_sim), None)
            if match is None:
                kept.append((day, source, item))
                words.append(text)
            else:
                agg.also_reported_by.setdefault(match[2].headline, []).append(source)
        agg.rows = kept
        return agg

    def by_date_range(self, start, end) -> AggregatedDigest:
        """Merged rows whose digest day is within [start, end] (str or date)."""
        agg = self.merged("windowed")
        lo, hi = str(start), str(end)
        agg.rows = [r for r in agg.rows if lo <= r[0].isoformat() <= hi]
        return agg


if __name__ == "__main__":
    from datetime import date
    from models import NewsItem
    agg = Aggregator()
    agg.add_source("aipulse", Digest(date(2026, 11, 5), [
        NewsItem("DOJ launches Super Intelligence Task Force", "Unit will prosecute AI misuse.")]))
    agg.add_source("wire", Digest(date(2026, 11, 6), [
        NewsItem("DOJ launches Super Intelligence Task Force unit", "The unit will prosecute AI misuse."),
        NewsItem("Nvidia falls 9 percent", "Chip rout deepens.")]))
    print("merged:", len(agg.merged().rows), "rows from", agg.merged().source_count, "sources",
          agg.merged().date_range)
    d = agg.dedupe_headlines()
    print("deduped:", [i.headline for i in d.items], d.also_reported_by)
    print("Nov 6 only:", [i.headline for i in agg.by_date_range("2026-11-06", "2026-11-06").items])
