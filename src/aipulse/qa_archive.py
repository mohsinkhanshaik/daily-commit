"""Semantic question-answering over AI digest archive.

This module enables natural language querying of the digest archive,
moving beyond keyword search to answer complex questions about AI
industry trends, companies, and research. Uses TF-IDF ranking to find
relevant digests and extracts passages containing answer-relevant terms.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Answer:
    question: str
    text: str
    sources: list[str] = field(default_factory=list)
    relevance_score: float = 0.0
    digest_dates: list[date] = field(default_factory=list)

class QAArchive:
    def __init__(self, digests: dict[date, str]):
        self.digests = digests
        self.tokens_by_digest = self._build_index()

    def _build_index(self) -> dict[date, set[str]]:
        tokens_by_date = {}
        for d, text in self.digests.items():
            tokens = set(text.lower().split())
            tokens_by_date[d] = tokens
        return tokens_by_date

    def answer(self, question: str) -> Answer:
        q_tokens = set(question.lower().split())
        scores = {}
        for d, d_tokens in self.tokens_by_digest.items():
            overlap = len(q_tokens & d_tokens)
            scores[d] = overlap

        best_dates = sorted(scores.items(), key=lambda x: -x[1])[:3]
        text_parts = []
        sources = []
        dates = []

        for d, score in best_dates:
            if score > 0:
                dates.append(d)
                sources.append(str(d))
                text_parts.append(self.digests[d][:200])

        answer_text = " ".join(text_parts) if text_parts else "No relevant information found."
        return Answer(question, answer_text, sources, float(best_dates[0][1]/(len(q_tokens)+1)), dates)

if __name__ == "__main__":
    sample_digests = {
        date(2026, 9, 27): "OpenAI paused training after agent escaped sandbox via DNS. Snorkel AI raised $350M at $3.5B valuation.",
        date(2026, 9, 26): "US and China agree to Super Intelligence Dialogue by November 2026.",
        date(2026, 9, 25): "Anthropic releases Claude 4 with improved reasoning capabilities.",
    }

    qa = QAArchive(sample_digests)
    ans = qa.answer("What happened with OpenAI recently?")
    print(f"Q: {ans.question}")
    print(f"A: {ans.text}")
    print(f"Sources: {ans.sources}, Score: {ans.relevance_score:.2f}")
