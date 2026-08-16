"""Watchlist module: track companies and AI models across digests.

Watchlist enables selective tracking of entities (companies, AI models) mentioned
in the digest archive. Users maintain a personal watchlist and retrieve a filtered
view of digest items mentioning their watched entities. Supports JSON export of
watchlist state for persistence and sharing.
"""

from dataclasses import dataclass, field
from typing import set
import json
from datetime import date
from models import NewsItem, Digest
from archive import DigestArchive


@dataclass
class Watchlist:
    """Personal entity watchlist for tracking companies and AI models.

    Attributes:
        companies: set of company names to track
        models: set of AI model names to track
    """
    companies: set = field(default_factory=set)
    models: set = field(default_factory=set)

    def add_company(self, name: str) -> None:
        """Add company to watchlist."""
        self.companies.add(name)

    def add_model(self, name: str) -> None:
        """Add AI model to watchlist."""
        self.models.add(name)

    def remove_company(self, name: str) -> None:
        """Remove company from watchlist."""
        self.companies.discard(name)

    def remove_model(self, name: str) -> None:
        """Remove AI model from watchlist."""
        self.models.discard(name)

    def filter_digest_items(self, items: list) -> list:
        """Filter news items mentioning watched entities.

        Args:
            items: list of NewsItem objects

        Returns:
            list of NewsItem objects matching watched entities
        """
        matching = []
        for item in items:
            for entity in item.entities:
                if entity in self.companies or entity in self.models:
                    matching.append(item)
                    break
        return matching

    def export_json(self) -> str:
        """Export watchlist to JSON."""
        return json.dumps({
            "companies": sorted(list(self.companies)),
            "models": sorted(list(self.models))
        }, indent=2)

    def watched_entities(self) -> set:
        """Return all watched entities as a single set."""
        return self.companies | self.models


if __name__ == "__main__":
    wl = Watchlist()
    wl.add_company("NVIDIA")
    wl.add_company("Meta")
    wl.add_model("Claude")
    wl.add_model("GPT-5")

    print("Watchlist entities:", wl.watched_entities())
    print("Companies:", sorted(wl.companies))
    print("Models:", sorted(wl.models))
    print("\nWatchlist JSON:")
    print(wl.export_json())

    sample_item = NewsItem(
        headline="NVIDIA releases new AI chips",
        summary="New hardware for inference",
        source="TechNews",
        url="https://example.com",
        entities=["NVIDIA", "chips"]
    )

    matching = wl.filter_digest_items([sample_item])
    print(f"\nFiltered {len(matching)} items matching watchlist")
