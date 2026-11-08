"""Extractive digest-of-digests: the top stories across a date range.

The day-13 module never ran. It imported names that do not exist
(digest_parser.parse_digest_file, scoring.score_items at the time), and
its "from .models" relative import fails whenever the file is run as a
script. Fixing the imports exposed four logic bugs, fixed here:

- load_digests() looked for files relative to the current directory and
  swallowed every exception; it now reads through archive.DigestArchive,
  which resolves the repo's digests/ folder and records parse errors.
- Ranking ignored dates, so a month-old story could outrank this week's.
  Items are scored with scoring.score(item, day, today=end) so recency
  counts against the end of the requested range.
- The same story covered on several days filled multiple top slots;
  near-duplicates (dedupe.py Jaccard >= 0.5) are collapsed, keeping the
  higher-scoring copy.
- The header claimed "Top stories from N days of coverage" where N was
  the number of ITEMS. It now reports days and stories separately, and
  each story keeps its date and its source URL.
"""

from datetime import date

from archive import DigestArchive
from dedupe import jaccard_similarity, normalize_text
from render import source_line
from scoring import score

DUP_THRESHOLD = 0.5


def load_digests(start, end, digests_dir=None):
    """[(day, Digest)] for start..end inclusive, oldest first."""
    archive = DigestArchive.load(digests_dir)
    return [(d.day, d) for d in archive.between(start, end)]


def extract_top_k(digests, k=10, today=None):
    """Top k (day, item, score) across digests, near-duplicates collapsed."""
    if not digests:
        return []
    today = today or max(day for day, _ in digests)
    ranked = sorted(((day, item, score(item, day, today)) for day, d in digests for item in d.items),
                    key=lambda row: (-row[2], row[0]))
    picked, seen = [], []
    for day, item, value in ranked:
        words = normalize_text(item.headline + " " + item.summary)
        if any(jaccard_similarity(words, w) >= DUP_THRESHOLD for w in seen):
            continue
        picked.append((day, item, value))
        seen.append(words)
        if len(picked) == k:
            break
    return picked


def render_summary_markdown(top, start, end, day_count):
    lines = ["# AI Pulse - Summary %s to %s" % (start, end), "",
             "Top %d stories from %d days of coverage, ranked by importance." % (len(top), day_count), ""]
    for day, item, value in top:
        lines += ["## %s" % item.headline,
                  "%s (%s, score %.1f)" % (item.summary, day.isoformat(), value),
                  source_line(item), ""]
    return "\n".join(lines).rstrip() + "\n"


def summarize_range(start, end, k=7, digests_dir=None):
    digests = load_digests(start, end, digests_dir)
    return render_summary_markdown(extract_top_k(digests, k), start, end, len(digests))


if __name__ == "__main__":
    print(summarize_range(date(2026, 10, 1), date(2026, 11, 7), k=5))
