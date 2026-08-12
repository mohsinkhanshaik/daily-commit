"""Near-duplicate story detection for AI Pulse digests.

Finds stories that are semantically similar (same topic, same event,
different coverage) to avoid redundancy in summary reports. Uses Jaccard
similarity on normalized n-grams to group closely related stories without
ML infrastructure.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class StoryCluster:
    """Group of semantically similar stories."""
    primary_headline: str
    stories: list[dict]
    similarity_threshold: float = 0.5


def normalize_text(text: str) -> str:
    """Lowercase and remove punctuation for similarity comparison."""
    return ''.join(c.lower() if c.isalnum() else ' ' for c in text)

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets of n-grams."""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def extract_ngrams(text: str, n: int = 3) -> set:
    """Extract n-grams from normalized text."""
    words = normalize_text(text).split()
    return {' '.join(words[i:i+n]) for i in range(len(words) - n + 1)}

def find_duplicates(stories: list[dict], threshold: float = 0.5) -> list[StoryCluster]:
    """Group stories by semantic similarity to find near-duplicates."""
    clusters = []
    used = set()
    for i, story_a in enumerate(stories):
        if i in used:
            continue
        cluster_stories = [story_a]
        used.add(i)
        ngrams_a = extract_ngrams(story_a.get('headline', ''))
        for j, story_b in enumerate(stories[i+1:], start=i+1):
            if j in used:
                continue
            ngrams_b = extract_ngrams(story_b.get('headline', ''))
            if jaccard_similarity(ngrams_a, ngrams_b) >= threshold:
                cluster_stories.append(story_b)
                used.add(j)
        if cluster_stories:
            clusters.append(StoryCluster(
                primary_headline=story_a.get('headline', 'Unknown'),
                stories=cluster_stories,
                similarity_threshold=threshold
            ))
    return clusters

if __name__ == '__main__':
    sample_stories = [
        {'headline': 'OpenAI releases GPT-5.6 Sol with advanced reasoning'},
        {'headline': 'OpenAI GPT-5.6 Sol breaches isolation in security test'},
        {'headline': 'Anthropic Claude Opus 5 half price of competitors'},
        {'headline': 'Claude Opus 5 pricing undercuts frontier models'},
    ]
    clusters = find_duplicates(sample_stories, threshold=0.4)
    for cluster in clusters:
        print(f"Primary: {cluster.primary_headline}")
        print(f"Group size: {len(cluster.stories)}")
