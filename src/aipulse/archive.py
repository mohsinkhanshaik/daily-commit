"""Archive module - load every digest and build a JSON index.

This is the entry point most analysis modules (search, stats, trends,
summarize, cli) sit on, so it has to be correct about three things:

1. Location. DEFAULT_DIR resolves to the repo's digests/ folder from this
   file's position, so the archive loads the same data no matter which
   directory a script is launched from (the old default 'digests' was
   relative to the cwd and silently returned an empty archive).
2. Types. load_archive() returns {"YYYY-MM-DD": Digest}. The previous
   docstring promised lists of NewsItem while the code stored Digest
   objects, so callers guessed differently and broke.
3. Failures. Unreadable or malformed files are collected in
   DigestArchive.errors instead of being swallowed by a bare except, and
   only real files named YYYY-MM-DD.md are read (a stray directory named
   2026-11-01.md used to be globbed as a digest).

DigestArchive wraps the dict with date-range queries and a JSON index
(build_index / write_index) that downstream tools can cache. By default
each loaded item is enriched with tagger.py's category and entities.py's
names, so every analysis module sees the same, accurate labels instead of
the parser's headline-only category guess and an empty entity list.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from digest_parser import parse_file
from entities import annotate
from tagger import tag_batch

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "digests"
NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


@dataclass
class DigestArchive:
    digests: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

    @classmethod
    def load(cls, digests_dir=None, enrich=True):
        """Parse every digest; enrich=True also tags categories and entities."""
        archive = cls()
        path = Path(digests_dir) if digests_dir else DEFAULT_DIR
        if not path.is_dir():
            archive.errors.append((str(path), "digests directory not found"))
            return archive
        for md_file in sorted(path.iterdir()):
            if not (md_file.is_file() and NAME_RE.match(md_file.name)):
                continue
            try:
                digest = parse_file(md_file)
                if enrich:
                    tag_batch(digest.items)
                    for item in digest.items:
                        annotate(item)
                archive.digests[md_file.stem] = digest
            except (OSError, ValueError, UnicodeDecodeError) as exc:
                archive.errors.append((md_file.name, str(exc)))
        return archive

    def days(self):
        return sorted(self.digests)

    def between(self, start, end):
        """Digests whose day is within [start, end]; accepts str or date."""
        lo, hi = str(start), str(end)
        return [self.digests[d] for d in self.days() if lo <= d <= hi]

    def all_digests(self):
        return [self.digests[d] for d in self.days()]

    def all_items(self):
        return [(d.day, item) for d in self.all_digests() for item in d.items]

    def build_index(self):
        """JSON-ready index: per-day counts, categories, headlines, urls."""
        days = []
        for digest in self.all_digests():
            days.append({
                "day": digest.day.isoformat(),
                "count": len(digest),
                "categories": sorted({i.category.value for i in digest.items}),
                "items": [{"headline": i.headline, "category": i.category.value,
                           "source": i.source, "url": i.url, "entities": i.entities}
                          for i in digest.items],
            })
        return {"days": days, "total_items": sum(d["count"] for d in days),
                "errors": [{"file": f, "error": e} for f, e in self.errors]}

    def write_index(self, out_path):
        Path(out_path).write_text(json.dumps(self.build_index(), indent=2), encoding="utf-8")


def load_archive(digests_dir=None):
    """Backward-compatible helper: {"YYYY-MM-DD": Digest}."""
    return DigestArchive.load(digests_dir).digests


def build_archive(digests_dir=None):
    """Load the archive and return its JSON index."""
    return DigestArchive.load(digests_dir).build_index()


def date_range_query(archive, start_date, end_date):
    """Filter a {day: Digest} dict to days within [start_date, end_date]."""
    lo, hi = str(start_date), str(end_date)
    return {d: v for d, v in archive.items() if lo <= d <= hi}


if __name__ == "__main__":
    arch = DigestArchive.load()
    index = arch.build_index()
    print("Archive: %d days, %d items, %d errors" % (
        len(index["days"]), index["total_items"], len(arch.errors)))
    for day in index["days"][-5:]:
        print("  %s: %d items %s" % (day["day"], day["count"], ",".join(day["categories"])))
