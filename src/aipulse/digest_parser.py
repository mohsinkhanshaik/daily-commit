"""Digest markdown parser - turns digests/YYYY-MM-DD.md into Digest objects.

The canonical digest format is:

    # AI Pulse - YYYY-MM-DD
    <intro line>
    ## <headline>
    <2-3 sentence summary ending with "Why it matters: ...">
    Source: Name (https://url)
    ... 5-7 sections ...
    Trend watch: <closing line>

The archive is older than the format, so the parser is deliberately
tolerant of the variants that really exist in digests/:
- "Source:" on its own line, indented, or inline at the end of the summary
  paragraph, and with several "Name (url)" pairs separated by commas;
- the closing line written as a "## Trend watch" heading, as
  "## Trend watch: text", or as a plain "Trend watch:" line;
- the older bullet style "- **Headline**: text" under topic headings such as
  "## Market & Funding", where each bullet is its own story.

Day resolution order: the "# AI Pulse - YYYY-MM-DD" header, then the
`day` argument (callers pass the filename date), then a long-form date in
the header ("November 2, 2026"). Raises ValueError when no day can be found
instead of silently building a Digest with no date.
"""

import re
from datetime import date, datetime

from models import Category, Digest, NewsItem

HEADER_RE = re.compile(r"^#\s+AI Pulse\s+-\s+(\d{4}-\d{2}-\d{2})\s*$")
LONG_DATE_RE = re.compile(r"([A-Z][a-z]+ \d{1,2}, \d{4})")
TREND_RE = re.compile(r"^(?:##\s*)?trend watch\s*:?\s*(.*)$", re.IGNORECASE)
SOURCE_SPLIT_RE = re.compile(r"(?:^|\s)Sources?:\s*", re.IGNORECASE)
URL_RE = re.compile(r"\((https?://[^)\s]+)\)")
BULLET_RE = re.compile(r"^[-*]\s+\*\*(.+?)\*\*\s*:?\s*(.*)$")

HEADING_CATEGORIES = [
    (("chip", "gpu", "hardware", "silicon", "semiconductor", "compute"), Category.CHIPS),
    (("fund", "invest", "raise", "valuation", "ipo", "market"), Category.FUNDING),
    (("policy", "govern", "regulat", "law", "export", "court", "doj"), Category.POLICY),
    (("research", "paper", "study", "benchmark"), Category.RESEARCH),
    (("model", "gpt", "claude", "gemini", "grok", "llama"), Category.MODELS),
    (("launch", "product", "app", "tool", "release"), Category.PRODUCTS),
]


def guess_category(headline):
    """Cheap headline-only category guess; tagger.py does the real work."""
    low = headline.lower()
    for cues, category in HEADING_CATEGORIES:
        if any(cue in low for cue in cues):
            return category
    return Category.OTHER


def split_source(text):
    """Split 'summary ... Source: Name (url)' into (summary, source, url)."""
    parts = SOURCE_SPLIT_RE.split(text, maxsplit=1)
    if len(parts) == 1:
        return text.strip(), "", ""
    summary, source = parts[0].strip(), parts[1].strip()
    match = URL_RE.search(source)
    url = match.group(1) if match else ""
    name = source[:match.start()].strip(" ,") if match else source
    return summary, name or source, url


def _make_item(headline, body, category=None):
    summary, source, url = split_source(" ".join(body).strip())
    return NewsItem(headline.strip(), summary, source, url,
                    category or guess_category(headline))


def _resolve_day(first_line, day):
    match = HEADER_RE.match(first_line.strip())
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    if isinstance(day, date):
        return day
    if isinstance(day, str) and day:
        return datetime.strptime(day, "%Y-%m-%d").date()
    long_form = LONG_DATE_RE.search(first_line)
    if long_form:
        return datetime.strptime(long_form.group(1), "%B %d, %Y").date()
    raise ValueError("digest has no '# AI Pulse - YYYY-MM-DD' header and no day given")


def parse_digest(markdown_text, day=None):
    """Parse digest markdown into a Digest (see module docstring)."""
    lines = [l.rstrip() for l in markdown_text.strip().splitlines()]
    if not lines:
        raise ValueError("empty digest")
    digest = Digest(day=_resolve_day(lines[0], day))
    heading, body, intro, in_trend = None, [], [], False

    def flush():
        if heading is not None and body:
            digest.add(_make_item(heading, body))

    for raw in lines[1:]:
        line = raw.strip()
        trend = TREND_RE.match(line)
        if trend:
            flush()
            heading, body, in_trend = None, [], True
            digest.trend_watch = trend.group(1).strip()
            continue
        if line.startswith("## "):
            flush()
            heading, body, in_trend = line[3:].strip(), [], False
            continue
        bullet = BULLET_RE.match(line)
        if bullet and heading is not None:
            digest.add(_make_item(bullet.group(1), [bullet.group(2)],
                                  guess_category(heading + " " + bullet.group(1))))
            continue
        if not line or line == "---":
            continue
        if heading is None:
            if in_trend:
                digest.trend_watch = (digest.trend_watch + " " + line).strip()
            else:
                intro.append(line)
        else:
            body.append(line)
    flush()
    digest.intro = " ".join(intro)
    return digest


def parse_file(filepath):
    """Parse a digest file; the filename date is the fallback day."""
    with open(filepath, "r", encoding="utf-8") as fh:
        text = fh.read()
    stem = str(filepath).replace("\\", "/").rsplit("/", 1)[-1][:10]
    fallback = stem if re.match(r"\d{4}-\d{2}-\d{2}$", stem) else None
    return parse_digest(text, fallback)


if __name__ == "__main__":
    sample = """# AI Pulse - 2026-07-21
Two launches and a mega-round.
## Grok 4.5 and GPT-5.6 ship in the same week
Four frontier launches in eight days. Why it matters: pace keeps rising.
    Source: Artificial Analysis (https://artificialanalysis.ai)
## Together AI raises 800M dollars
Series C closed. Why it matters: infra keeps getting big checks. Source: VentureBeat (https://venturebeat.com/x)
## Trend watch
Cost, not raw capability, is the battleground.
"""
    d = parse_digest(sample)
    print(d.day, len(d), "items | intro:", d.intro)
    for item in d.items:
        print(" -", item.category.value, "|", item.headline, "|", item.source, "|", item.url)
    print("trend:", d.trend_watch)
