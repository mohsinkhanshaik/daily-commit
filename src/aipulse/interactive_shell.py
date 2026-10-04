"""Interactive REPL for exploring AI Pulse digest archive.

Provides a Python REPL built on the cmd module with readline support.
Users run queries, filter results, and iterate on analysis logic interactively.
Session context (digest list, search results) persists across commands.
"""

import cmd
import json
import datetime
from typing import List, Dict


class Shell(cmd.Cmd):
    """Interactive shell for AI Pulse digest exploration."""

    intro = "AI Pulse Explorer. Type help or ? for commands. quit to exit."
    prompt = "pulse> "

    def __init__(self):
        super().__init__()
        self.current_digests: List[Dict] = []
        self.search_results: List[Dict] = []
        self.last_filter_date: str = ""

    def do_search(self, arg):
        """search-cmd: Search digests by keyword (usage: search <keyword>)"""
        if not arg:
            print("Usage: search <keyword>")
            return
        self.search_results = [d for d in self.current_digests
                               if arg.lower() in str(d).lower()]
        print(f"Found {len(self.search_results)} results for '{arg}'")

    def do_filter(self, arg):
        """filter-cmd: Filter digests by date (usage: filter <YYYY-MM-DD>)"""
        if not arg:
            print("Usage: filter <YYYY-MM-DD>")
            return
        self.last_filter_date = arg
        self.current_digests = [d for d in self.current_digests
                                if d.get('date', '') >= arg]
        print(f"Filtered to {len(self.current_digests)} digests")

    def do_view(self, arg):
        """view-cmd: View current digest list or search results"""
        items = self.search_results if self.search_results else self.current_digests
        if not items:
            print("No digests loaded. Load some first.")
            return
        for i, d in enumerate(items[:5], 1):
            print(f"{i}. {d.get('headline', 'N/A')} ({d.get('date', 'N/A')})")
        if len(items) > 5:
            print(f"... and {len(items) - 5} more")

    def do_trends(self, arg):
        """trends-cmd: Compute trends across loaded digests"""
        if not self.current_digests:
            print("No digests loaded.")
            return
        categories = {}
        for d in self.current_digests:
            cat = d.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        print("Category trends:", json.dumps(categories, indent=2))

    def do_help(self, arg):
        """help-cmd: Show all available commands"""
        print("Commands: search, filter, view, trends, help, quit")
        super().do_help(arg)

    def do_quit(self, arg):
        """quit-cmd: Exit the shell"""
        print("Goodbye!")
        return True

    do_EOF = do_quit


if __name__ == "__main__":
    shell = Shell()
    sample_data = [
        {"date": "2026-10-04", "headline": "OpenAI solves Navier-Stokes", "category": "research"},
        {"date": "2026-10-03", "headline": "Google releases Gemini 4", "category": "models"},
        {"date": "2026-10-02", "headline": "AMD acquires World Labs", "category": "funding"},
    ]
    shell.current_digests = sample_data
    shell.cmdloop()
