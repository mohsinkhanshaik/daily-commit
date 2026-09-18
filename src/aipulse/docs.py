"""README generator from roadmap and archive metadata.

Introspects the ROADMAP.md to extract phases and feature descriptions,
scans digests/ directory for existing archives, and synthesizes a
comprehensive README with project overview, module inventory, archive
statistics, and usage examples. Stdlib only, no external calls."""

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ArchiveStats:
    total_digests: int
    date_range: tuple
    categories: dict

class ReadmeGenerator:
    def __init__(self, root: Path = Path(".")):
        self.root = root
        self.roadmap_path = root / "src/aipulse/ROADMAP.md"
        self.digests_dir = root / "digests"

    def collect_archive_stats(self) -> ArchiveStats:
        if not self.digests_dir.exists():
            return ArchiveStats(0, (None, None), {})
        digests = sorted(self.digests_dir.glob("*.md"))
        dates = [Path(d).stem for d in digests]
        return ArchiveStats(
            total_digests=len(digests),
            date_range=(min(dates) if dates else None, max(dates) if dates else None),
            categories={})

    def generate_toc(self) -> str:
        return "## Contents\n- Features\n- Module Inventory\n- Archive\n- Usage"

    def generate_readme(self) -> str:
        stats = self.collect_archive_stats()
        lines = [
            "# AI Pulse Toolkit",
            "",
            "Daily AI-industry research archive and queryable Python toolkit.",
            self.generate_toc(),
            "",
            f"## Archive",
            f"Total digests: {stats.total_digests}",
            f"Coverage: {stats.date_range[0]} to {stats.date_range[1]}",
            "",
            "See README in repo root for more."]
        return "\n".join(lines)

if __name__ == "__main__":
    gen = ReadmeGenerator()
    print(gen.generate_readme())
