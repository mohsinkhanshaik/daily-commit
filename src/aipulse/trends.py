"""Term frequency across time windows.

term_frequency() used to split on whitespace and count every token, so
the "trending terms" were always 'the', 'and', 'of' and 'why' (from every
"Why it matters:" sentence). Terms are now lowercase word tokens with
stopwords and digest boilerplate removed, counted once per item (document
frequency), so one long story cannot dominate a window.

window_frequency() is the time-window API the module docstring always
promised: it takes (day, item) pairs, keeps the last `days` days ending at
`end`, and returns the term counts for that window.
"""

import re
from collections import Counter
from datetime import timedelta

STOPWORDS = set("""a about after again all also an and any are as at be because been before
being between both but by can could did do does each for from had has have he her his how
i if in into is it its just more most new no not now of on one only or other our out over
said says so some such than that the their them then there these they this those through
to too under up very was we were what when where which while who why will with would year
years percent dollars billion million matters it's ai week first""".split())
_WORD = re.compile(r"[a-z][a-z0-9\-]+")


def terms_of(text):
    return {w for w in _WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 2}


def term_frequency(items, min_count=2):
    """{term: number of items mentioning it} for terms seen >= min_count times."""
    counter = Counter()
    for item in items:
        counter.update(terms_of(item.headline + " " + item.summary))
    return {t: c for t, c in counter.items() if c >= min_count}


def window_frequency(dated_items, end, days=7, min_count=2):
    """term_frequency over (day, item) pairs with end - days < day <= end."""
    start = end - timedelta(days=days)
    return term_frequency([item for day, item in dated_items if start < day <= end], min_count)


def top_terms(tf_dict, limit=10):
    """Top N (term, count) pairs, ties broken alphabetically."""
    return sorted(tf_dict.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]


if __name__ == "__main__":
    from archive import DigestArchive
    rows = DigestArchive.load().all_items()
    end = max(day for day, _ in rows)
    print("Top terms, 30 days to", end)
    for term, count in top_terms(window_frequency(rows, end, days=30), 12):
        print("  %-14s %d" % (term, count))
