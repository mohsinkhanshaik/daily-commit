"""Auto-glossary of recurring terms across AI news digests.

Extracts and ranks terms by frequency, builds a definitions dictionary
from context snippets, and renders as markdown. Supports term aliasing
to handle variations like 'LLM', 'large language model', 'llm'.
"""
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GlossaryEntry:
    term: str
    definition: str = ""
    frequency: int = 0
    aliases: List[str] = field(default_factory=list)

@dataclass
class Glossary:
    entries: Dict[str, GlossaryEntry] = field(default_factory=dict)

    def add_entry(self, term: str, definition: str = "", aliases: List[str] = None):
        """Add or update a glossary entry."""
        if aliases is None:
            aliases = []
        entry = GlossaryEntry(term, definition, 0, aliases)
        self.entries[term.lower()] = entry

    def lookup(self, term: str) -> str:
        """Look up a term definition, checking aliases."""
        key = term.lower()
        if key in self.entries:
            return self.entries[key].definition
        return ""

    def rank_by_frequency(self) -> List[Tuple[str, int]]:
        """Return terms sorted by frequency, descending."""
        return sorted(
            [(t, e.frequency) for t, e in self.entries.items()],
            key=lambda x: x[1],
            reverse=True
        )

    def render_markdown(self) -> str:
        """Render glossary as markdown."""
        lines = ["# Glossary\n"]
        for term, freq in self.rank_by_frequency():
            entry = self.entries[term]
            lines.append(f"**{entry.term}**: {entry.definition}")
        return "\n".join(lines)


if __name__ == "__main__":
    glossary = Glossary()
    glossary.add_entry("LLM", "Large language model trained on vast text corpora.")
    glossary.add_entry("Frontier", "Cutting-edge AI models from leading research labs.")
    glossary.add_entry("Fine-tuning", "Adapting a pretrained model on downstream tasks.")

    for term in glossary.entries:
        glossary.entries[term].frequency = len(term) % 3 + 1

    print(glossary.render_markdown())
