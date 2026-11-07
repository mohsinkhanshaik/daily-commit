"""aipulse command-line interface over the real toolkit.

The day-16 CLI parsed arguments and then printed canned strings: `search`
echoed the query, `trends` echoed the window size, and `status` always
reported "16 digests, updated 2026-08-07" no matter what was on disk.
Every command now runs the corresponding module against the parsed,
tagged archive (loaded once through cache.cached_archive):

    status     days, stories, date span, parse errors, category mix
    search     ranked keyword search (search.py)
    browse     recent stories in one category
    trends     top terms in the last N days (trends.py)
    momentum   rising/falling terms, last N weeks vs the N weeks before
    compare    two date ranges side by side (compare.py)
    summary    top stories across a range (summarize.py)
    watch      timeline of chosen companies/models (watchlist.py)
    validate   lint digest files (validate.py); exit 1 on errors

Dates default to the newest digest, not the wall clock, so output is
reproducible. Use --digests to point at another folder.
"""

import argparse
import json
import sys
from datetime import date, timedelta

from cache import cached_archive
from compare import compare, key_differences
from models import Category
from momentum import compute_momentum
from search import Query, search
from stats import category_share
from summarize import extract_top_k, render_summary_markdown
from trends import top_terms, window_frequency
from watchlist import Watchlist
import validate


def create_parser():
    p = argparse.ArgumentParser(prog="aipulse", description="Query the AI Pulse digest archive")
    p.add_argument("--digests", help="digests folder (default: repo digests/)")
    sub = p.add_subparsers(dest="command")
    s = sub.add_parser("status"); s.add_argument("--format", choices=["text", "json"], default="text")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=10)
    s.add_argument("--category", choices=[c.value for c in Category])
    s = sub.add_parser("browse"); s.add_argument("category", choices=[c.value for c in Category])
    s.add_argument("--days", type=int, default=14)
    s = sub.add_parser("trends"); s.add_argument("--days", type=int, default=30)
    s.add_argument("--top", type=int, default=15)
    s = sub.add_parser("momentum"); s.add_argument("--weeks", type=int, default=4)
    s = sub.add_parser("compare")
    for name in ("start1", "end1", "start2", "end2"):
        s.add_argument(name, type=date.fromisoformat)
    s = sub.add_parser("summary"); s.add_argument("start", type=date.fromisoformat)
    s.add_argument("end", type=date.fromisoformat); s.add_argument("--top", type=int, default=7)
    s = sub.add_parser("watch"); s.add_argument("names", nargs="+")
    s = sub.add_parser("validate"); s.add_argument("paths", nargs="*")
    return p


def run(args, out=print):
    if args.command == "validate":
        return validate.main(args.paths or ([args.digests] if args.digests else []))
    arch = cached_archive(args.digests)
    digests = arch.all_digests()
    if not digests:
        out("No digests found."); return 1
    newest = digests[-1].day
    if args.command == "status":
        info = {"days": len(digests), "stories": sum(len(d) for d in digests),
                "first": digests[0].day.isoformat(), "latest": newest.isoformat(),
                "parse_errors": len(arch.errors), "category_share": category_share(digests)}
        out(json.dumps(info, indent=2) if args.format == "json" else
            "\n".join("%-15s %s" % kv for kv in info.items()))
    elif args.command == "search":
        cat = Category(args.category) if args.category else None
        for r in search(digests, Query(args.query, category=cat))[:args.limit]:
            out("%.2f  %-8s %s" % (r.relevance_score, r.item.category.value, r.item.headline))
    elif args.command == "browse":
        for d in arch.between(newest - timedelta(days=args.days), newest):
            for item in d.by_category(args.category):
                out("%s  %s" % (d.day, item.headline))
    elif args.command == "trends":
        for term, n in top_terms(window_frequency(arch.all_items(), newest, args.days), args.top):
            out("%-18s %d" % (term, n))
    elif args.command == "momentum":
        span = 7 * args.weeks
        rows = arch.all_items()
        now = window_frequency(rows, newest, span, min_count=1)
        before = window_frequency(rows, newest - timedelta(days=span), span, min_count=1)
        rising, falling = compute_momentum(before, now)
        rising = [r for r in rising if now.get(r[0], 0) >= 3][:10]
        falling = [f for f in falling if before.get(f[0], 0) >= 3][:10]
        out("rising:  " + ", ".join("%s(%d)" % (t, now[t]) for t, _ in rising))
        out("falling: " + ", ".join("%s(%+.0f%%)" % (t, 100 * c) for t, c in falling))
    elif args.command == "compare":
        res = compare(arch, (args.start1, args.end1), (args.start2, args.end2))
        for line in key_differences(res):
            out(line)
    elif args.command == "summary":
        picked = [(d.day, d) for d in arch.between(args.start, args.end)]
        out(render_summary_markdown(extract_top_k(picked, args.top), args.start, args.end, len(picked)))
    elif args.command == "watch":
        wl = Watchlist(models=set(args.names))
        wl.companies = set(args.names)
        for name, rows in wl.hits_over_time(digests).items():
            out("%s: %d stories" % (name, len(rows)))
            for day, headline in rows[-5:]:
                out("  %s  %s" % (day, headline))
    return 0


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
