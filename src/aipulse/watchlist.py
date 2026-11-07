"""Watchlist: track chosen companies and AI models across the archive.

The day-21 module never ran: "from typing import set" raises ImportError,
and it imported DigestArchive from archive.py before that class existed.
With imports fixed, the matching itself was the bigger problem:

- It only looked at item.entities, which the parser leaves empty, so a
  real digest never matched anything. Entities are now extracted from
  headline + summary when missing (entities.py).
- Matching was exact and case-sensitive: watching "NVIDIA" missed
  "Nvidia", and watching "Claude" missed "Claude Fable 5.1". Names are
  compared case-insensitively, and a watched model name matches any model
  that starts with it ("GPT-6" matches "GPT-6 Cyber").
- export_json() had no load counterpart, so the "persistence" in the
  docstring was one-way; from_json() and save()/load() complete it.
- hits_over_time() answers the question a watchlist exists for: on which
  days did each watched name appear, and in which headlines.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from entities import extract_entities


def _names(item):
    if item.entities:
        return list(item.entities)
    return extract_entities(item.headline + " " + item.summary).all()


@dataclass
class Watchlist:
    companies: set = field(default_factory=set)
    models: set = field(default_factory=set)

    def add_company(self, name):
        self.companies.add(name)

    def add_model(self, name):
        self.models.add(name)

    def remove_company(self, name):
        self.companies.discard(name)

    def remove_model(self, name):
        self.models.discard(name)

    def watched_entities(self):
        return self.companies | self.models

    def matches(self, item):
        """Watched names this item mentions."""
        found = {n.lower() for n in _names(item)}
        hits = {c for c in self.companies if c.lower() in found}
        hits |= {m for m in self.models if any(f == m.lower() or f.startswith(m.lower() + " ")
                                               for f in found)}
        return sorted(hits)

    def filter_digest_items(self, items):
        return [i for i in items if self.matches(i)]

    def hits_over_time(self, digests):
        """{watched name: [(day, headline), ...]} in chronological order."""
        out = {name: [] for name in sorted(self.watched_entities())}
        for digest in sorted(digests, key=lambda d: d.day):
            for item in digest.items:
                for name in self.matches(item):
                    out[name].append((digest.day, item.headline))
        return out

    def export_json(self):
        return json.dumps({"companies": sorted(self.companies),
                           "models": sorted(self.models)}, indent=2)

    @classmethod
    def from_json(cls, text):
        data = json.loads(text)
        return cls(set(data.get("companies", [])), set(data.get("models", [])))

    def save(self, path):
        Path(path).write_text(self.export_json(), encoding="utf-8")

    @classmethod
    def load(cls, path):
        return cls.from_json(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    from archive import DigestArchive
    wl = Watchlist({"NVIDIA", "Anthropic"}, {"GPT-6", "Kimi K3"})
    assert Watchlist.from_json(wl.export_json()) == wl
    hits = wl.hits_over_time(DigestArchive.load().all_digests())
    for name, rows in hits.items():
        last = "%s %s" % (rows[-1][0], rows[-1][1][:50]) if rows else "-"
        print("%-10s %3d stories | latest: %s" % (name, len(rows), last))
