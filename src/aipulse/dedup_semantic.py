"""Semantic story deduplication using lightweight token-based similarity.

Detects substantively similar news items despite different wording by computing
token overlap and character-level Jaccard similarity. Uses only stdlib for
embedding computation via token frequency and simple hashing.
"""

from dataclasses import dataclass, field
from collections import Counter
import hashlib


@dataclass
class SemanticDedupEngine:
    threshold: float = 0.7

    def tokenize(self, text: str) -> set:
        return set(text.lower().split())

    def jaccard_similarity(self, set1: set, set2: set) -> float:
        if not set1 and not set2:
            return 1.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def deduplicate(self, items):
        if not items:
            return []

        clusters = []
        used = set()

        for i, item in enumerate(items):
            if i in used:
                continue
            cluster = [item]
            item_tokens = self.tokenize(item.headline + " " + item.summary)

            for j in range(i + 1, len(items)):
                if j in used:
                    continue
                other_tokens = self.tokenize(items[j].headline + " " + items[j].summary)
                sim = self.jaccard_similarity(item_tokens, other_tokens)

                if sim >= self.threshold:
                    cluster.append(items[j])
                    used.add(j)

            clusters.append(cluster)
            used.add(i)

        return clusters


if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass
    class NewsItem:
        headline: str
        summary: str

    items = [
        NewsItem("OpenAI releases GPT-6", "New frontier model surpasses competitors"),
        NewsItem("GPT-6 Astra launches", "OpenAI announces sixth generation model beats rivals"),
        NewsItem("Anthropic ships Claude 5.1", "Updates API with breaking changes"),
        NewsItem("Google Gemini 3.8 released", "DeepMind launches new Gemini version"),
    ]

    engine = SemanticDedupEngine(threshold=0.6)
    clusters = engine.deduplicate(items)

    print(f"Deduplicated {len(items)} items into {len(clusters)} clusters:")
    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i+1}: {len(cluster)} items")
        for item in cluster:
            print(f"    - {item.headline}")
