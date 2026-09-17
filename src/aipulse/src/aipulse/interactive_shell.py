"""Interactive REPL for exploring AI news data archive.

Provides a cmd-based shell for querying the digest archive in real-time.
Users can search digests, filter by date, view trends, and explore patterns
without writing standalone scripts. Maintains session state across commands.
"""

import cmd
import json
import datetime
from pathlib import Path


class AINewsShell(cmd.Cmd):
    """Interactive shell for AI news archive exploration."""

    intro = "AI News Interactive Shell - type 'help' for commands"
    prompt = "aipulse> "

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []
        self.current_digests = []
        self.date_filter = None

    def do_search(self, arg):
        """search QUERY - search for keyword in digest headlines."""
        if not arg:
            print("Usage: search QUERY")
            return
        self.results = [d for d in self.current_digests 
                       if arg.lower() in d.get("headline", "").lower()]
        print(f"Found {len(self.results)} matches for '{arg}'")
        for r in self.results[:5]:
            print(f"  - {r.get('headline', 'N/A')}")

    def do_filter(self, arg):
        """filter DATE - filter digests by YYYY-MM-DD date."""
        if not arg:
            print("Usage: filter YYYY-MM-DD")
            return
        self.date_filter = arg
        print(f"Filter set to {arg}")

    def do_view(self, arg):
        """view - display current results."""
        if not self.results:
            print("No results. Try 'search' first.")
            return
        for i, r in enumerate(self.results, 1):
            print(f"{i}. {r.get('headline')} ({r.get('date')})")

    def do_trends(self, arg):
        """trends - show top keywords from current results."""
        if not self.results:
            print("No results. Try 'search' first.")
            return
        words = {}
        for r in self.results:
            for word in r.get("headline", "").split():
                words[word] = words.get(word, 0) + 1
        top = sorted(words.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top trends:")
        for word, count in top:
            print(f"  {word}: {count}")

    def do_quit(self, arg):
        """quit - exit the shell."""
        print("Goodbye!")
        return True

    def emptyline(self):
        """Override to do nothing on empty input."""
        pass


def load_sample_digests():
    """Load sample digest data for demo."""
    return [
        {"date": "2026-09-17", "headline": "Claude Fable 5.1 released with faster inference",
         "category": "models"},
        {"date": "2026-09-17", "headline": "OpenAI and Anthropic in AI safety talks",
         "category": "policy"},
        {"date": "2026-09-16", "headline": "NVIDIA acquires Groq for 20 billion",
         "category": "chips"},
        {"date": "2026-09-16", "headline": "Google Gemini 3.8 surpasses GPT-5.5",
         "category": "models"},
        {"date": "2026-09-15", "headline": "AI Pulse archive hits 35 days",
         "category": "products"},
    ]


if __name__ == "__main__":
    shell = AINewsShell()
    shell.current_digests = load_sample_digests()
    print(f"Loaded {len(shell.current_digests)} sample digests")
    shell.cmdloop()
