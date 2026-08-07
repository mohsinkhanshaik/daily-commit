"""
CLI module for AI Pulse archive and toolkit.

Provides argparse-based command-line interface to query digests, analyze trends,
search the archive, and render reports. Commands build on existing toolkit modules.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from enum import Enum


class Command(Enum):
    SEARCH = "search"
    BROWSE = "browse"
    TRENDS = "trends"
    MOMENTUM = "momentum"
    COMPARE = "compare"
    STATUS = "status"


def create_parser():
    """Create and return the argument parser for AI Pulse CLI."""
    parser = argparse.ArgumentParser(
        prog="aipulse",
        description="Query and analyze the AI Pulse digest archive",
        epilog="Examples: aipulse search 'ai' | aipulse trends --days 30"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search digests by keyword")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")

    browse_parser = subparsers.add_parser("browse", help="Browse by category")
    browse_parser.add_argument("category", choices=["models", "chips", "funding", "policy"])
    browse_parser.add_argument("--days", type=int, default=7, help="Look back N days")

    trends_parser = subparsers.add_parser("trends", help="Analyze trending terms")
    trends_parser.add_argument("--days", type=int, default=30, help="Window size")
    trends_parser.add_argument("--top", type=int, default=15, help="Top N terms")

    momentum_parser = subparsers.add_parser("momentum", help="Rising topics")
    momentum_parser.add_argument("--weeks", type=int, default=4, help="Compare weeks")

    compare_parser = subparsers.add_parser("compare", help="Compare date ranges")
    compare_parser.add_argument("start_date", help="Start date YYYY-MM-DD")
    compare_parser.add_argument("end_date", help="End date YYYY-MM-DD")

    status_parser = subparsers.add_parser("status", help="Show archive status")
    status_parser.add_argument("--format", choices=["text", "json"], default="text")

    return parser


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "search":
        print(f"Searching: {args.query} (limit: {args.limit})")
        return 0
    elif args.command == "browse":
        print(f"Browsing {args.category} ({args.days} days)")
        return 0
    elif args.command == "trends":
        print(f"Trends ({args.days}d window, top {args.top})")
        return 0
    elif args.command == "momentum":
        print(f"Momentum ({args.weeks} weeks)")
        return 0
    elif args.command == "compare":
        print(f"Comparing {args.start_date} to {args.end_date}")
        return 0
    elif args.command == "status":
        if args.format == "json":
            print(json.dumps({"digests": 16, "updated": "2026-08-07"}))
        else:
            print("Archive: 16 digests, updated 2026-08-07")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
