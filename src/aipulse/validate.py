"""Digest format linter for AI Pulse.

Validates digest markdown files against the standard format:
header with date, intro line, 5-7 sections with headlines and summaries,
each ending with "Why it matters:" and "Source: name (url)",
and a closing "Trend watch:" line. Reports all format violations.
"""

import re
from pathlib import Path
from typing import List, Tuple

def load_digest_file(path: str) -> str:
    """Load digest markdown file and return content."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        raise FileNotFoundError(f"Digest file not found: {path}")

def validate_format(digest_text: str) -> List[str]:
    """Validate digest format. Return list of error messages."""
    errors = []
    lines = digest_text.split('\n')

    if not lines or not lines[0].startswith('# AI Pulse -'):
        errors.append("Missing header: '# AI Pulse - YYYY-MM-DD'")

    section_count = len([l for l in lines if l.startswith('##')])
    if section_count < 5:
        errors.append(f"Too few sections: {section_count}, need 5-7")
    if section_count > 7:
        errors.append(f"Too many sections: {section_count}, need 5-7")

    for i, line in enumerate(lines):
        if line.startswith('##'):
            has_why = False
            has_source = False
            for j in range(i+1, min(i+10, len(lines))):
                if 'Why it matters:' in lines[j]:
                    has_why = True
                if lines[j].startswith('Source:'):
                    has_source = True
            if not has_why:
                errors.append(f"Section '{line[:50]}': missing 'Why it matters:'")
            if not has_source:
                errors.append(f"Section '{line[:50]}': missing 'Source:'")

    if not any('Trend watch:' in line for line in lines):
        errors.append("Missing closing 'Trend watch:' line")

    return errors

if __name__ == "__main__":
    digest_path = "digests/2026-08-13.md"
    try:
        content = load_digest_file(digest_path)
        errors = validate_format(content)
        if errors:
            print(f"Validation errors in {digest_path}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"{digest_path} is valid.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
