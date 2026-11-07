"""Question answering over the digest archive with source attribution.

The day-40 demo crashed with "TypeError: '<' not supported between
instances of 'dict' and 'dict'": search() sorted (score, item) tuples, and
whenever two items tied on score Python fell through to comparing the
dicts. Fixing the sort exposed the real accuracy problems, fixed here:

- Zero-overlap items were returned as answers. Any question got three
  "sources" even when nothing matched; results below MIN_SCORE are dropped
  and answer() says so honestly.
- Jaccard similarity against the whole story punished long, detailed
  items (a bigger union) and rewarded short ones. Scoring is now a
  TF-IDF-weighted overlap: rare query words ("Wyoming", "DOJ") count far
  more than common ones ("AI", "new"), and stopwords count for nothing.
- Headline matches weigh double, since headlines state the story.
- Confidence was recomputed per result with a different formula from the
  ranking; it is now the top result's score, normalized to [0, 1].

from_archive() builds the index straight from a DigestArchive.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field

STOPWORDS = set("""a an and are as at be by for from has have in is it its of on or that the
this to was were what which who will with about latest recent how why when did does do
any there their than then they them into over after new ai""".split())
MIN_SCORE = 0.05
_WORD = re.compile(r"[a-z0-9][a-z0-9.\-]*[a-z0-9]|[a-z0-9]")


def tokenize(text):
    return [w for w in _WORD.findall(text.lower()) if w not in STOPWORDS]


@dataclass
class Answer:
    question: str
    text: str
    sources: list = field(default_factory=list)
    confidence: float = 0.0

    def __str__(self):
        cites = " | ".join("%s (%s)" % s for s in self.sources) or "No sources"
        return "%s\n\nSources: %s\nConfidence: %.2f" % (self.text, cites, self.confidence)


class SemanticQA:
    def __init__(self, archive_items=None):
        self.items = list(archive_items or [])
        self._df = None

    def add_item(self, date_str, headline, summary, source_url):
        self.items.append({"date": str(date_str), "headline": headline, "summary": summary,
                           "url": source_url, "head": Counter(tokenize(headline)),
                           "body": Counter(tokenize(summary))})
        self._df = None

    @classmethod
    def from_archive(cls, archive):
        qa = cls()
        for day, item in archive.all_items():
            qa.add_item(day, item.headline, item.summary, item.url or item.source)
        return qa

    def _idf(self, word):
        if self._df is None:
            self._df = Counter(w for it in self.items for w in set(it["head"]) | set(it["body"]))
        return math.log((1 + len(self.items)) / (1 + self._df.get(word, 0))) + 1.0

    def _score(self, query, item):
        if not query:
            return 0.0
        hit = sum(self._idf(w) * (2.0 * (w in item["head"]) + (w in item["body"])) for w in query)
        best = sum(self._idf(w) * 3.0 for w in query)
        return hit / best

    def search(self, query, top_k=3):
        terms = set(tokenize(query))
        scored = [(self._score(terms, it), i) for i, it in enumerate(self.items)]
        scored = [(s, i) for s, i in scored if s >= MIN_SCORE]
        scored.sort(key=lambda pair: self.items[pair[1]]["date"], reverse=True)  # newest first...
        scored.sort(key=lambda pair: pair[0], reverse=True)  # ...within equal scores (stable)
        return [(round(s, 3), self.items[i]) for s, i in scored[:top_k]]

    def answer(self, question, top_k=3):
        results = self.search(question, top_k)
        if not results:
            return Answer(question, "No relevant information found in the archive.", [], 0.0)
        lines = ["%s - %s: %s" % (it["date"], it["headline"], it["summary"]) for _, it in results]
        return Answer(question, "Most relevant coverage:\n" + "\n".join(lines),
                      [(it["headline"], it["url"]) for _, it in results], results[0][0])


if __name__ == "__main__":
    qa = SemanticQA()
    qa.add_item("2026-09-29", "Claude Sonnet 5.5 Outperforms",
                "Anthropic shipped Claude Sonnet 5.5 with 30% faster generation.", "https://llm-stats.com")
    qa.add_item("2026-09-29", "OpenAI Agents Bypass Security",
                "OpenAI disclosed 24 incidents where agents defeated safety controls.", "https://aiweekly.co")
    qa.add_item("2026-09-29", "Chip Sales Jump 135%",
                "Global semiconductor sales hit $146.8B in July 2026.", "https://semiconductors.org")
    for q in ("What did Anthropic ship?", "How fast are chip sales growing?", "Who won the World Cup?"):
        print("Q:", q)
        print(qa.answer(q), "\n")
