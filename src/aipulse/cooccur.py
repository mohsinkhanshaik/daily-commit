"""Entity co-occurrence analysis for news stories.

Identifies which entities (companies, models) appear together in the same news
item, enabling relationship mapping and narrative tracking across digests. The
analyze_cooccurrences function scans all items, counts entity pairs, and returns
them ranked by frequency for timeline analysis.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List

@dataclass
class CooccurrencePair:
    entity_a: str
    entity_b: str
    count: int
    start_date: date
    end_date: date

def analyze_cooccurrences(digest_list, min_threshold=1):
    """Count entity co-occurrences across digests.

    Returns list of CooccurrencePair objects sorted by frequency descending.
    Each pair represents entities appearing in the same news item headline or
    summary. Pairs are deduplicated (entity_a, entity_b) vs (entity_b, entity_a).
    """
    pair_map = {}
    date_range = {}

    for digest in digest_list:
        for item in digest.items:
            entities = sorted(item.entities) if hasattr(item, 'entities') else []
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    key = tuple(sorted([entities[i], entities[j]]))
                    if key not in pair_map:
                        pair_map[key] = 0
                        date_range[key] = [digest.day, digest.day]
                    pair_map[key] += 1
                    date_range[key][1] = digest.day

    result = []
    for (ent_a, ent_b), count in sorted(pair_map.items(), key=lambda x: -x[1]):
        if count >= min_threshold:
            result.append(CooccurrencePair(
                ent_a, ent_b, count,
                date_range[(ent_a, ent_b)][0],
                date_range[(ent_a, ent_b)][1]
            ))

if __name__ == "__main__":
    from src.aipulse.models import Digest, NewsItem, Category

    sample = Digest(date(2026, 8, 1))
    sample.add(NewsItem("OpenAI and DeepSeek lead", "", "", entities=["OpenAI", "DeepSeek"]))
    sample.add(NewsItem("Nvidia and AMD compete", "", "", entities=["Nvidia", "AMD"]))

    pairs = analyze_cooccurrences([sample])
    print(f"Top pairs: {len(pairs)} found")
    for pair in pairs[:3]:
        print(f"  {pair.entity_a} <-> {pair.entity_b}: {pair.count}")
    return result
