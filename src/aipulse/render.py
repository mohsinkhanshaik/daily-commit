"""Render Digest objects back to canonical digest markdown.

The day-15 renderer could not be imported from the toolkit (it used
`from aipulse.models import ...` while every other module uses flat
imports), and render_by_category() called digest.by_category() with no
argument, which raised TypeError on the old Digest. Both are fixed, and
the renderer now produces the full canonical format so that
render_digest(parse_digest(text)) round-trips:

- the intro line and the closing "Trend watch:" line are emitted (they
  were dropped, so a rendered digest failed validate.py);
- "Source: Name (url)" is written exactly as the parser reads it;
- categories render in a fixed editorial order instead of dict order.
"""

from models import Category, Digest

ORDER = [Category.MODELS, Category.CHIPS, Category.FUNDING, Category.POLICY,
         Category.RESEARCH, Category.PRODUCTS, Category.OTHER]


def source_line(item):
    name = item.source or "Unknown"
    return "Source: %s (%s)" % (name, item.url) if item.url else "Source: " + name


def render_digest(digest: Digest) -> str:
    lines = ["# AI Pulse - " + digest.day.isoformat(), ""]
    if digest.intro:
        lines += [digest.intro, ""]
    if not digest.items:
        lines.append("No items recorded for this date.")
    for item in digest.items:
        lines += ["## " + item.headline, item.summary, source_line(item), ""]
    if digest.trend_watch:
        lines.append("Trend watch: " + digest.trend_watch)
    return "\n".join(lines).rstrip() + "\n"


def render_by_category(digest: Digest) -> dict:
    """{category value: markdown block}, in editorial ORDER."""
    grouped = digest.by_category()
    result = {}
    for cat in ORDER:
        if cat not in grouped:
            continue
        lines = ["## " + cat.value.title(), ""]
        for item in grouped[cat]:
            lines += ["### " + item.headline, item.summary, source_line(item), ""]
        result[cat.value] = "\n".join(lines).rstrip() + "\n"
    return result


if __name__ == "__main__":
    from archive import DEFAULT_DIR
    from digest_parser import parse_digest
    from validate import validate_format
    text = (DEFAULT_DIR / "2026-11-07.md").read_text(encoding="utf-8")
    digest = parse_digest(text)
    rendered = render_digest(digest)
    again = parse_digest(rendered)
    same = [(i.headline, i.summary, i.url) for i in digest.items] == \
           [(i.headline, i.summary, i.url) for i in again.items]
    errors = [f for f in validate_format(rendered, "2026-11-07.md") if f[0] == "ERROR"]
    print("round-trip identical:", same, "| validator errors:", len(errors))
    print("categories:", list(render_by_category(digest)))
    print(rendered[:300])
