"""Interactive REPL for exploring AI news data.

Provides a command-line interface to query digests, search items, explore
trends, and analyze the AI Pulse archive. Loads from json index (archive.py)
and provides commands like search, trend, entities, category, top.
"""

import json
import cmd
import glob
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class PulseREPL(cmd.Cmd):
    """Interactive shell for AI Pulse archive exploration."""

    intro = "AI Pulse REPL - type 'help' for commands, 'quit' to exit"
    prompt = "pulse> "

    def __init__(self):
        super().__init__()
        self.items = []
        self.load_archive()

    def load_archive(self):
        """Load items from digests directory."""
        digest_files = glob.glob('digests/*.md')
        for fpath in sorted(digest_files):
            try:
                with open(fpath) as f:
                    content = f.read()
                    self.items.append({'date': Path(fpath).stem, 'content': content})
            except:
                pass

    def do_search(self, arg):
        """search KEYWORD - find items mentioning keyword."""
        if not arg:
            print("Usage: search <keyword>")
            return
        matches = [i for i in self.items if arg.lower() in i['content'].lower()]
        print(f"Found {len(matches)} matches for '{arg}'")
        for item in matches[:5]:
            print(f"  {item['date']}")

    def do_count(self, arg):
        """count - total items in archive."""
        print(f"Archive contains {len(self.items)} digest items")

    def do_recent(self, arg):
        """recent [N] - show last N digests (default 5)."""
        n = int(arg) if arg else 5
        for item in self.items[-n:]:
            print(f"  {item['date']}")

    def do_categories(self, arg):
        """categories - list common sections across digests."""
        sections = defaultdict(int)
        for item in self.items:
            for line in item['content'].split('\n'):
                if line.startswith('##'):
                    sections[line.strip()] += 1
        for sect, cnt in sorted(sections.items(), key=lambda x: -x[1])[:10]:
            print(f"  {sect} ({cnt})")

if __name__ == '__main__':
    repl = PulseREPL()
    print("Explore AI Pulse archive: search OpenAI, count items, recent digests")
    print("Type 'help' for all commands.\n")
    repl.cmdloop()
