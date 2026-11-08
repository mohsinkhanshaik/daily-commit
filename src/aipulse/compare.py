"""Compare two date ranges of the digest archive.

The day-14 compare() never looked at the archive: it returned hard-coded
numbers (new_items_count = 5, removed_items_count = 2, topic_shifts =
{"AI funding": +15, "Chips": +8}) for ANY input, and the CLI printed them
as if they were analysis. Every figure is now computed from real digests:

- story counts and digest-day counts for each range;
- per-category deltas (range2 minus range1), from the tagged categories;
- entity deltas plus entities that appear only in the later range
  ("newcomers") or only in the earlier one ("dropped").

"New" and "removed" stories were never meaningful for two different date
ranges (no story is in both), so they are replaced by the counts above.
"""

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ComparisonResult:
    range1: tuple
    range2: tuple
    days1: int = 0
    days2: int = 0
    items1: int = 0
    items2: int = 0
    category_shift: dict = field(default_factory=dict)
    entity_shift: dict = field(default_factory=dict)
    newcomers: list = field(default_factory=list)
    dropped: list = field(default_factory=list)

    def summary(self):
        return ("%s..%s (%d days, %d stories) vs %s..%s (%d days, %d stories)" %
                (self.range1[0], self.range1[1], self.days1, self.items1,
                 self.range2[0], self.range2[1], self.days2, self.items2))


def _profile(digests):
    cats, ents = Counter(), Counter()
    for d in digests:
        for item in d.items:
            cats[item.category.value] += 1
            ents.update(set(item.entities))
    return cats, ents


def _delta(a, b):
    keys = set(a) | set(b)
    return {k: b.get(k, 0) - a.get(k, 0) for k in sorted(keys) if b.get(k, 0) != a.get(k, 0)}


def compare(archive, range1, range2):
    """Compare two (start, end) ranges of a DigestArchive."""
    first, second = archive.between(*range1), archive.between(*range2)
    c1, e1 = _profile(first)
    c2, e2 = _profile(second)
    return ComparisonResult(
        tuple(map(str, range1)), tuple(map(str, range2)),
        len(first), len(second),
        sum(len(d) for d in first), sum(len(d) for d in second),
        _delta(c1, c2), _delta(e1, e2),
        sorted(set(e2) - set(e1), key=lambda k: (-e2[k], k)),
        sorted(set(e1) - set(e2), key=lambda k: (-e1[k], k)))


def key_differences(result, limit=5):
    lines = [result.summary()]
    for cat, delta in sorted(result.category_shift.items(), key=lambda kv: -abs(kv[1])):
        lines.append("category %-9s %+d" % (cat, delta))
    movers = sorted(result.entity_shift.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:limit]
    lines += ["entity   %-16s %+d" % kv for kv in movers]
    if result.newcomers:
        lines.append("newcomers: " + ", ".join(result.newcomers[:limit]))
    return lines


if __name__ == "__main__":
    from archive import DigestArchive
    arch = DigestArchive.load()
    res = compare(arch, ("2026-08-01", "2026-08-31"), ("2026-09-01", "2026-09-30"))
    print("\n".join(key_differences(res)))
