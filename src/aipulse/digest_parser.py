"""Digest markdown parser - converts markdown files into Digest model objects."""
import re
from datetime import datetime
from models import Digest, NewsItem, Category


def parse_digest(markdown_text: str) -> Digest:
    """Parse digest markdown into a Digest object."""
    lines = markdown_text.strip().split('\n')
    digest = Digest()

    # Extract date from first line (# AI Pulse - YYYY-MM-DD)
    if lines and lines[0].startswith('# AI Pulse -'):
        date_str = lines[0].split(' - ')[1].strip()
        try:
            digest.day = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, IndexError):
            pass

    # Parse sections (## heading followed by content)
    current_section = None
    current_text = []

    for line in lines[1:]:
        if line.startswith('## '):
            # Save previous section
            if current_section and current_text:
                item = _parse_section(current_section, '\n'.join(current_text))
                if item:
                    digest.items.append(item)
            current_section = line[3:].strip()
            current_text = []
        elif line.strip():
            current_text.append(line)

    # Save last section
    if current_section and current_text:
        item = _parse_section(current_section, '\n'.join(current_text))
        if item:
            digest.items.append(item)

    return digest

def _parse_section(headline: str, text: str) -> NewsItem:
    """Parse a single section into a NewsItem."""
    summary_lines = []
    source = ''
    category = Category.OTHER
    entities = []

    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith('Source:'):
            source = line[7:].strip()
        elif line.startswith('Why it matters:'):
            summary_lines.append(line[15:].strip())
        elif not line.strip() or line.startswith('Trend watch:'):
            continue
        else:
            summary_lines.append(line.strip())

    # Determine category from headline
    headline_lower = headline.lower()
    if 'chip' in headline_lower or 'gpu' in headline_lower or 'hardware' in headline_lower:
        category = Category.CHIPS
    elif 'fund' in headline_lower or 'invest' in headline_lower or 'round' in headline_lower:
        category = Category.FUNDING
    elif 'policy' in headline_lower or 'govern' in headline_lower or 'regul' in headline_lower:
        category = Category.POLICY
    elif 'research' in headline_lower or 'paper' in headline_lower or 'study' in headline_lower:
        category = Category.RESEARCH
    elif 'model' in headline_lower or 'release' in headline_lower or 'launch' in headline_lower:
        category = Category.PRODUCTS

    summary = ' '.join(summary_lines)[:500]
    return NewsItem(headline, summary, source, category=category, entities=entities)

def parse_file(filepath: str) -> Digest:
    """Parse a digest markdown file and return a Digest object."""
    with open(filepath, 'r') as f:
        return parse_digest(f.read())


if __name__ == '__main__':
    sample = '''# AI Pulse - 2026-07-21
## Model Releases
Four frontier launches occurred in eight days: Grok 4.5, GPT-5.6, and others. Why it matters: Competition accelerates pace of innovation.
    Source: artificialanalysis.ai
## Funding Announcements
Together AI raised $800M Series C. Why it matters: Major infra plays continue getting big checks.
    Source: venturebeat.com
'''
    digest = parse_digest(sample)
    print(f'Digest for {digest.day}: {len(digest.items)} items')
    for item in digest.items:
        print(f'  - {item.headline[:50]}... ({item.category.value})')
