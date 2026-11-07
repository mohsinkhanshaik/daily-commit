"""Digest format linter for AI Pulse.

Checks digests/YYYY-MM-DD.md files against the canonical format documented
in digest_parser.py. The linter parses with the same parser the rest of the
toolkit uses, so "valid" means "the toolkit reads it the way it was meant",
instead of a second, drifting set of line-by-line regexes.

Findings are (level, message) pairs. ERROR means the toolkit will lose or
misread data (no header, wrong date, missing sources). WARN marks legacy
style that still parses (a "## Trend watch" heading, a source without a
URL, non-ASCII punctuation). The old linter flagged every "## Trend watch"
heading as a broken news section, never noticed inline "Source:" text, and
looked for digests relative to the current directory; all three are fixed.

Run: python validate.py [files or directories...]  (default: the repo's
digests/ folder). Exit status is 1 when any ERROR is found, so it can gate CI.
"""

import re
import sys
from pathlib import Path

from digest_parser import HEADER_RE, parse_digest

REPO_DIGESTS = Path(__file__).resolve().parents[2] / "digests"
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def validate_format(text, filename=None):
    """Return a list of (level, message) findings for one digest's text."""
    found = []
    lines = text.strip().splitlines()
    if not lines or not HEADER_RE.match(lines[0].strip()):
        found.append(("ERROR", "first line must be '# AI Pulse - YYYY-MM-DD'"))
    name_match = FILENAME_RE.match(filename or "")
    try:
        digest = parse_digest(text, name_match.group(1) if name_match else None)
    except ValueError as exc:
        return found + [("ERROR", str(exc))]
    if name_match and digest.day.isoformat() != name_match.group(1):
        found.append(("ERROR", "header date %s does not match filename" % digest.day))
    if not digest.intro:
        found.append(("WARN", "missing intro line under the header"))
    if not 5 <= len(digest) <= 7:
        found.append(("ERROR", "%d news sections, expected 5-7" % len(digest)))
    for item in digest.items:
        label = "section '%s'" % item.headline[:50]
        if "why it matters:" not in item.summary.lower():
            found.append(("ERROR", label + " has no 'Why it matters:' sentence"))
        if not item.source:
            found.append(("ERROR", label + " has no 'Source:' line"))
        elif not item.url:
            found.append(("WARN", label + " source has no (https://...) URL"))
    if not digest.trend_watch:
        found.append(("ERROR", "missing closing 'Trend watch:' line"))
    elif re.search(r"^##\s*trend watch", text, re.IGNORECASE | re.MULTILINE):
        found.append(("WARN", "'Trend watch' written as a heading; use a plain line"))
    bad = sorted({ch for ch in text if ord(ch) > 127})
    if bad:
        found.append(("WARN", "non-ASCII characters: %s" % " ".join(repr(c) for c in bad)))
    return found


def iter_digest_files(paths):
    """Expand files and directories (recursively) into digest .md files."""
    for path in map(Path, paths):
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*.md") if p.is_file())
        elif path.is_file():
            yield path


def main(argv):
    targets = argv or [str(REPO_DIGESTS)]
    errors = 0
    for path in iter_digest_files(targets):
        text = path.read_text(encoding="utf-8", errors="replace")
        for level, message in validate_format(text, path.name):
            errors += level == "ERROR"
            print("%s %s: %s" % (level, path.name, message))
    print("%d error(s)" % errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
