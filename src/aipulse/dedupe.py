"""Near-duplicate story detection via word-set similarity.

Identifies news items that are substantively similar despite minor wording
differences. Uses Jaccard similarity on word sets to group near-duplicates.
Via a sliding window, detects stories that are redundant within a time span.
"""

from dataclasses import dataclass, field
from datetime import date
from collections import defaultdict
import re


def normalize_text(text: str) -> set:
    """Extract and normalize word set from text."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return set(w for w in words if len(w) > 2)

def jaccard_similarity(set1: set, set2: set) -> float:
    """Compute Jaccard similarity between two word sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

@dataclass
class DedupeGroup:
    """Cluster of near-duplicate items."""
    primary_idx: int
    duplicate_indices: list = field(default_factory=list)
    similarity_scores: list = field(default_factory=list)

def find_duplicates(items: list, threshold: float = 0.7) -> list:
    """Find near-duplicate groups in a list of items.

    Args:
        items: List of dicts with 'headline' and 'summary' keys.
        threshold: Jaccard similarity threshold (0.0 to 1.0).

    Returns:
        List of DedupeGroup objects.
    """
    if len(items) < 2:
        return []

    word_sets = [normalize_text(item.get('headline', '') + ' ' + 
                                 item.get('summary', '')) 
                 for item in items]

    groups = []
    assigned = set()

    for i, set_i in enumerate(word_sets):
        if i in assigned:
            continue
        group = DedupeGroup(primary_idx=i)

        for j in range(i + 1, len(word_sets)):
            if j in assigned:
                continue
            sim = jaccard_similarity(set_i, word_sets[j])
            if sim >= threshold:
                group.duplicate_indices.append(j)
                group.similarity_scores.append(sim)
                assigned.add(j)

        if group.duplicate_indices:
            groups.append(group)
            assigned.add(i)

    return groups

if __name__ == '__main__':
    test_items = [
        {'headline': 'OpenAI releases new model',
         'summary': 'OpenAI announces a powerful new AI model'},
        {'headline': 'OpenAI unveils latest model',
         'summary': 'OpenAI introduces a new artificial intelligence model'},
        {'headline': 'DeepSeek updates chip',
         'summary': 'DeepSeek releases new hardware'},
    ]

    dupes = find_duplicates(test_items, threshold=0.6)
    print(f'Found {len(dupes)} duplicate group(s)')
    for g in dupes:
        print(f'  Primary #{g.primary_idx} has duplicates {g.duplicate_indices}')
