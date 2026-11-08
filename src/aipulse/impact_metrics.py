"""Impact metrics: which entities gain or lose prominence over time.

The day-43 file never imported: every line after the dataclass header was
indented one level deeper than the previous one (an IndentationError at
line 15). Beyond the indentation, the logic had three bugs, fixed here:

- impact_window() hard-coded trend='stable' for every entity, so the
  "trend" field never carried information. The window is now split into
  an earlier and a later half and the trend comes from comparing them.
- compare_impact() stored int(new_score) as `mentions`, mixing a 0-100
  normalized score into a raw count field. Mentions are now real counts.
- Dates were parsed with datetime.strptime on every loop iteration and
  compared as datetimes; date objects and ISO strings are both accepted.

Score: mentions normalized to the top entity in the window (0-100).
Trend: 'rising' / 'falling' when the share of mentions in the later half
moves by more than TREND_DELTA percentage points versus the earlier half,
'new' when an entity is absent from the earlier half, else 'stable'.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

TREND_DELTA = 10.0


@dataclass
class EntityImpact:
    entity: str
    score: float
    mentions: int
    trend: str


def _as_date(value):
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def _counts(entities_by_date, start, end):
    counts = Counter()
    for day, names in entities_by_date.items():
        if start <= _as_date(day) <= end:
            counts.update(names)
    return counts


def _share(counts):
    total = sum(counts.values()) or 1
    return {name: 100.0 * n / total for name, n in counts.items()}


def classify(before_share, after_share, name):
    if name not in before_share:
        return "new"
    change = after_share.get(name, 0.0) - before_share[name]
    if change > TREND_DELTA:
        return "rising"
    if change < -TREND_DELTA:
        return "falling"
    return "stable"


def impact_window(entities_by_date, start, end):
    """EntityImpact list for [start, end], highest score first."""
    lo, hi = _as_date(start), _as_date(end)
    counts = _counts(entities_by_date, lo, hi)
    if not counts:
        return []
    mid = lo + timedelta(days=(hi - lo).days // 2)
    before = _share(_counts(entities_by_date, lo, mid))
    after = _share(_counts(entities_by_date, mid + timedelta(days=1), hi))
    top = max(counts.values())
    impacts = [EntityImpact(name, round(100.0 * n / top, 1), n, classify(before, after, name))
               for name, n in counts.items()]
    return sorted(impacts, key=lambda e: (-e.score, e.entity))


def compare_impact(earlier, later):
    """Trajectory between two impact_window() results, biggest risers first."""
    old = {e.entity: e for e in earlier}
    new = {e.entity: e for e in later}
    rows = []
    for name in set(old) | set(new):
        before = old[name].score if name in old else 0.0
        after = new[name].score if name in new else 0.0
        trend = "new" if name not in old else ("rising" if after - before > TREND_DELTA else
                                               "falling" if before - after > TREND_DELTA else "stable")
        rows.append((after - before, EntityImpact(name, after, new[name].mentions if name in new else 0, trend)))
    return [impact for _, impact in sorted(rows, key=lambda r: (-r[0], r[1].entity))]


def entities_by_day(digests):
    """{date: [entity, ...]} from parsed digests, extracting when needed."""
    from entities import extract_entities
    out = {}
    for d in digests:
        names = []
        for item in d.items:
            names += item.entities or extract_entities(item.headline + " " + item.summary).all()
        out[d.day] = names
    return out


if __name__ == "__main__":
    data = {"2026-11-01": ["OpenAI", "Nvidia", "Anthropic"],
            "2026-11-02": ["OpenAI", "Nvidia"],
            "2026-11-03": ["Nvidia", "Anthropic", "DeepSeek"],
            "2026-11-04": ["Anthropic", "DeepSeek", "Anthropic"]}
    for e in impact_window(data, "2026-11-01", "2026-11-04"):
        print("%-10s score=%5.1f mentions=%d %s" % (e.entity, e.score, e.mentions, e.trend))
