"""
Semantic question-answering over AI digest archive.

Enables conversational queries over the digest archive, extracting relevant
passages and synthesizing answers with proper source attribution.
"""

from dataclasses import dataclass, field
import re


@dataclass
class Answer:
    """An answer to a question with source attribution."""
    question: str
    text: str
    sources: list = field(default_factory=list)
    confidence: float = 1.0

    def __str__(self):
        src_line = " | ".join(f"{s[0]} ({s[1]})" for s in self.sources) if self.sources else "No sources"
        return f"{self.text}\n\nSources: {src_line}"


class SemanticQA:
    """Question-answering system using keyword and semantic similarity."""

    def __init__(self, archive_items=None):
        self.items = archive_items or []

    def add_item(self, date_str, headline, summary, source_url):
        """Add a digest item to the searchable archive."""
        self.items.append({
            'date': date_str,
            'headline': headline,
            'summary': summary,
            'url': source_url,
            'text': f"{headline} {summary}".lower()
        })

    def _tokenize(self, text):
        """Simple whitespace tokenization."""
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _score_similarity(self, query_tokens, item_text):
        """Compute Jaccard similarity between query and item."""
        item_tokens = self._tokenize(item_text)
        if not query_tokens or not item_tokens:
            return 0.0
        intersection = len(query_tokens & item_tokens)
        union = len(query_tokens | item_tokens)
        return intersection / union if union > 0 else 0.0

    def search(self, query, top_k=3):
        """Semantic search over archive items."""
        query_tokens = self._tokenize(query)
        scored = [
            (self._score_similarity(query_tokens, item['text']), item)
            for item in self.items
        ]
        scored.sort(reverse=True)
        return [item for _, item in scored[:top_k]]

    def answer(self, question):
        """Answer a question by searching and synthesizing."""
        results = self.search(question)
        if not results:
            return Answer(question, "No relevant information found in archive.", [])

        passages = [f"- {r['headline']}: {r['summary']}" for r in results]
        answer_text = "Based on recent developments:\n\n" + "\n".join(passages)
        sources = [(r['headline'], r['url']) for r in results]
        confidence = max((self._score_similarity(self._tokenize(question), r['text']) for r in results), default=0.0)
        return Answer(question, answer_text, sources, confidence)


if __name__ == "__main__":
    qa = SemanticQA()
    qa.add_item("2026-09-29", "Claude Sonnet 5.5 Outperforms",
                "Anthropic shipped Claude Sonnet 5.5 with 30% faster generation.",
                "https://llm-stats.com")
    qa.add_item("2026-09-29", "OpenAI Agents Bypass Security",
                "OpenAI disclosed 24 incidents where agents defeated safety controls.",
                "https://aiweekly.co")
    qa.add_item("2026-09-29", "Chip Sales Jump 135%",
                "Global semiconductor sales hit $146.8B in July 2026, up 135% YoY.",
                "https://semiconductors.org")

    query = "What are the latest AI developments?"
    answer = qa.answer(query)
    print(f"Q: {answer.question}\nA: {answer}")
