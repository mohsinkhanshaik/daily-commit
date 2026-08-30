"""README generator from roadmap and archive metadata.

Generates polished markdown README from the project roadmap and digest
archive metadata, automating project documentation and onboarding narrative.
Covers phases, quickstart, feature list, archive browsing, and CLI usage."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from datetime import date

@dataclass
class ReadmeConfig:
    """Configuration for README generation."""
    project_name: str = "AI Pulse"
    project_desc: str = "Daily AI-industry research into a queryable archive"
    roadmap_path: str = "src/aipulse/ROADMAP.md"
    archive_path: str = "digests"
    output_path: str = "README.md"

def from_roadmap(config: ReadmeConfig) -> str:
    """Extract phases and features from ROADMAP.md."""
    try:
        with open(config.roadmap_path) as f:
            content = f.read()
    except FileNotFoundError:
        return "## Roadmap\n\nRoadmap not yet available."

    lines = [l for l in content.split('\n') if l.strip()]
    phases = []
    current_phase = None

    for line in lines:
        if line.startswith('Phase'):
            current_phase = line
            phases.append((current_phase, []))
        elif line.startswith('Day ') and phases:
            phases[-1][1].append(line)

    result = "## Roadmap\n\n"
    for phase, days in phases:
        result += f"### {phase}\n\n"
        for day in days[:5]:
            result += f"- {day}\n"
        if len(days) > 5:
            result += f"- ... and {len(days)-5} more\n"
        result += "\n"
    return result

def from_archive(config: ReadmeConfig) -> str:
    """Summarize the digest archive."""
    archive_dir = Path(config.archive_path)
    if not archive_dir.exists():
        return "## Archive\n\nNo digests yet."

    digests = sorted(archive_dir.glob("*.md"))
    count = len(digests)
    if count == 0:
        return "## Archive\n\nNo digests yet."

    earliest = digests[0].stem
    latest = digests[-1].stem

    result = f"## Archive\n\n"
    result += f"**{count} daily digests** from {earliest} to {latest}.\n\n"
    result += "Browse the archive: `ls digests/` or visit "
    result += f"[digests/](digests/) to explore past AI news summaries.\n"
    return result

def make_quickstart() -> str:
    """Generate a quickstart example."""
    qs = "## Quickstart\n\n"
    qs += "```bash\n"
    qs += "python -m aipulse.cli search -q 'transformer models' -n 5\n"
    qs += "python -m aipulse.cli trends --days 7\n"
    qs += "python -m aipulse.cli timeline --entity 'OpenAI'\n"
    qs += "```\n\n"
    qs += "See [cli.py](src/aipulse/cli.py) for full command reference.\n"
    return qs

def generate(config: ReadmeConfig = None) -> str:
    """Assemble the complete README."""
    config = config or ReadmeConfig()

    readme = f"# {config.project_name}\n\n"
    readme += f"{config.project_desc}, built one feature per day.\n\n"
    readme += "## Installation\n\n"
    readme += "```bash\ngit clone https://github.com/mohsinkhanshaik/daily-commit\n"
    readme += "cd daily-commit\npython -m pip install -e .\n```\n\n"
    readme += make_quickstart()
    readme += from_roadmap(config)
    readme += from_archive(config)
    readme += "\n## Contributing\n\n"
    readme += "Each day adds one toolkit feature plus a researched AI digest.\n"
    return readme

if __name__ == "__main__":
    config = ReadmeConfig()
    readme = generate(config)
    print(readme)
    with open(config.output_path, "w") as f:
        f.write(readme)
    print(f"\nREADME written to {config.output_path}")
