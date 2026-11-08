"""Cross-digest relevance: persistent themes versus one-off stories.

The day-41 module was committed to src/aipulse/src/aipulse/relevance_scorer.py,
outside the package, and crashed at import with "TypeError: 'items' is a
field but has no type annotation" (a dataclass field needs an annotation).
Behind that were two logic bugs, fixed here:

- theme_frequency() compared item dates (date objects) against
  datetime.now() - timedelta(...), a TypeError, and measured "recent"
  against the wall clock, so the same archive scored differently every
  day. The window is now relative to the digest being scored.
- rank_by_relevance() divided the prior-week category count by the size
  of the CURRENT digest, so a 9-item day looked less persistent than a
  5-item day with the same history. Persistence is now the share of the
  previous WINDOW_DAYS of stories that belong to the same category,
  blended with how similar the story is to those earlier headlines.

Score = 0.5 * category persistence + 0.5 * max cosine similarity of the
story to any story in the preceding window (both in [0, 1]).
"""

import math
import re
from collections import Counter
from datetime import timedelta

WINDOW_DAYS = 7
_WORD = re.compile(r"[a-z0-9]{3,}")


def tokens(text):
    return Counter(_WORD.findall(text.lower()))


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(a[w] * b[w] for w in a.keys() & b.keys())
    return dot / math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))


def rank_by_relevance(digests, window_days=WINDOW_DAYS):
    """[(item, score, day)] for every item, most persistent first."""
    history = []  # (day, category, token counter)
    ranked = []
    for digest in sorted(digests, key=lambda d: d.day):
        start = digest.day - timedelta(days=window_days)
        recent = [h for h in history if start <= h[0] < digest.day]
        cats = Counter(h[1] for h in recent)
        for item in digest.items:
            vec = tokens(item.headline + " " + item.summary)
            persistence = cats[item.category] / len(recent) if recent else 0.0
            echo = max((cosine(vec, h[2]) for h in recent), default=0.0)
            ranked.append((item, round(0.5 * persistence + 0.5 * echo, 3), digest.day))
        history += [(digest.day, i.category, tokens(i.headline + " " + i.summary))
                    for i in digest.items]
    return sorted(ranked, key=lambda r: (-r[1], r[2]))


if __name__ == "__main__":
    from archive import DigestArchive
    rows = rank_by_relevance(DigestArchive.load().all_digests())
    print("Most persistent themes:")
    for item, score, day in rows[:5]:
        print("  %.3f %s %s" % (score, day, item.headline[:70]))
