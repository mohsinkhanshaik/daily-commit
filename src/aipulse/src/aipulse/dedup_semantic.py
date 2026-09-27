"""Semantic deduplication engine using embedding-based similarity.

Day 39: Semantic story deduplication engine

This module implements semantic deduplication using TF-IDF-based embeddings
and cosine similarity to detect substantively similar stories despite
textual differences. Builds on Day 18 (simple hash-based dedup) with
learnable semantic matching for multi-source news archives.
"""

from dataclasses import dataclass, field
from collections import Counter
import math

@dataclass
class DedupCluster:
    """Cluster of similar stories with metadata."""
    representative: 'NewsItem'
    members: list = field(default_factory=list)
    similarity_scores: dict = field(default_factory=dict)

def tf_idf_vector(text: str, idf_cache: dict) -> dict:
    """Compute TF-IDF vector from text."""
    tokens = text.lower().split()
    if not tokens:
        return {}

    term_freq = Counter(tokens)
    doc_len = len(tokens)
    tf_vector = {term: freq / doc_len for term, freq in term_freq.items()}

    tfidf = {}
    for term, tf_val in tf_vector.items():
        idf = idf_cache.get(term, 1.0)
        tfidf[term] = tf_val * idf

    return tfidf

def cosine_similarity(vec1: dict, vec2: dict) -> float:
    """Compute cosine similarity between TF-IDF vectors."""
    common_terms = set(vec1.keys()) & set(vec2.keys())
    if not common_terms:
        return 0.0

    dot_product = sum(vec1[t] * vec2[t] for t in common_terms)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

class SemanticDedupEngine:
    """Semantic deduplication using embedding-based similarity."""

    def __init__(self, threshold: float = 0.7):
        """Initialize engine with similarity threshold (0-1)."""
        self.threshold = threshold
        self.idf_cache = {}

    def build_idf_cache(self, texts: list) -> None:
        """Build IDF cache from corpus of texts."""
        if not texts:
            return

        doc_freq = Counter()
        all_terms = set()

        for text in texts:
            terms = set(text.lower().split())
            doc_freq.update(terms)
            all_terms.update(terms)

        total_docs = len(texts)
        self.idf_cache = {
            term: math.log(total_docs / doc_freq[term]) 
            for term in all_terms
        }

    def deduplicate(self, items: list) -> list:
        """Deduplicate items using semantic similarity."""
        if not items:
            return []

        texts = [getattr(item, 'headline', '') + ' ' + 
                getattr(item, 'summary', '') for item in items]
        self.build_idf_cache(texts)

        vectors = [tf_idf_vector(text, self.idf_cache) for text in texts]

        clusters = []
        used = set()

        for i, item in enumerate(items):
            if i in used:
                continue

            cluster = DedupCluster(representative=item)
            cluster.members.append(item)
            used.add(i)

            for j in range(i + 1, len(items)):
                if j in used:
                    continue

                sim = cosine_similarity(vectors[i], vectors[j])
                if sim >= self.threshold:
                    cluster.members.append(items[j])
                    cluster.similarity_scores[j] = sim
                    used.add(j)

            clusters.append(cluster)

        return [c.representative for c in clusters]

if __name__ == '__main__':
    class MockItem:
        def __init__(self, headline, summary):
            self.headline = headline
            self.summary = summary

        def __repr__(self):
            return f"Item({self.headline[:40]}...)"

    items = [
        MockItem('OpenAI releases GPT-6 Astra', 
                'Frontier reasoning model with 97% MathBench score'),
        MockItem('OpenAI launches GPT-6 reasoning model', 
                'New frontier model scores 99.9% on benchmarks'),
        MockItem('Google releases Gemini 3.8 Flash', 
                'Competitive model at comparable pricing'),
        MockItem('Meta releases new LLM in September', 
                'Muse Spark 1.3 advances coding capabilities'),
    ]

    engine = SemanticDedupEngine(threshold=0.65)
    deduplicated = engine.deduplicate(items)

    print(f"Input: {len(items)} items")
    print(f"Output: {len(deduplicated)} deduplicated items")
    for item in deduplicated:
        print(f"  - {item}")
