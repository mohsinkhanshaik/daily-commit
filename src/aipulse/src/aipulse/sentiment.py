"""Lexicon-based sentiment scoring for news items.

Sentiment scoring uses word-level positive/negative associations to measure
tone across news digests. Handles negation (not good = bad) and intensifiers
(very bad = more negative). Lexicon-imperfect for sarcasm; assumes text is
factual news language.

Key design: flat structure, single SentimentLexicon class, pure functions."""

from dataclasses import dataclass


BUILTIN_LEXICON = {
    "breakthrough": 2, "surge": 2, "surge": 2, "soar": 2, "success": 2,
    "launch": 1, "release": 1, "announce": 1, "record": 1, "lead": 1,
    "funding": 1, "growth": 1, "expand": 1, "partner": 1, "collaborate": 1,
    "fail": -2, "crash": -2, "down": -1, "risk": -1, "concern": -1,
    "decline": -1, "loss": -1, "issue": -1, "challenge": -1, "delay": -1,
    "scandal": -2, "collapse": -2, "ban": -2, "warn": -1, "critical": -1,
    "threat": -1, "obsolete": -2, "exploit": -2, "hacked": -2, "vulnerable": -1,
}

INTENSIFIERS = {"very", "extremely", "highly", "significantly", "dramatically"}
NEGATORS = {"not", "no", "never", "barely"}


@dataclass
class SentimentScore:
    """Result of sentiment analysis."""
    positive_count: int
    negative_count: int
    neutral_count: int

    def label(self):
        """Return sentiment label: positive, negative, or neutral."""
        if self.positive_count > self.negative_count:
            return "positive"
        elif self.negative_count > self.positive_count:
            return "negative"
        else:
            return "neutral"


class SentimentLexicon:
    """Sentiment lexicon for scoring news text."""

    def __init__(self, lexicon=None):
        """Initialize with custom or built-in lexicon."""
        self.lexicon = lexicon if lexicon else BUILTIN_LEXICON.copy()

    @classmethod
    def from_file(cls, path):
        """Load lexicon from file (word<tab>score, one per line)."""
        lex = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) == 2:
                    word, score = parts[0].lower(), int(parts[1])
                    lex[word] = score
        return cls(lex)

    def score_text(self, text):
        """Score text; return SentimentScore."""
        text_lower = text.lower()
        words = text_lower.split()

        pos, neg, neut = 0, 0, 0
        i = 0
        while i < len(words):
            word = words[i].strip(".,!?;:")

            # Check negation context
            negated = i > 0 and words[i-1].strip(".,!?;:") in NEGATORS
            intensity = 1
            if i > 0 and words[i-1].strip(".,!?;:") in INTENSIFIERS:
                intensity = 2

            if word in self.lexicon:
                score = self.lexicon[word]
                if negated:
                    score = -score
                score *= intensity
                if score > 0:
                    pos += score
                elif score < 0:
                    neg += -score
                else:
                    neut += 1
            else:
                neut += 1
            i += 1

        return SentimentScore(pos, neg, neut)


if __name__ == "__main__":
    lex = SentimentLexicon()

    # Test three headlines from different categories
    headlines = [
        "Cerebras announces 281% YoY growth in Q2 cloud revenue",
        "Google Gemini 3.5 Pro delayed after testing failures expose risks",
        "Anthropic raises Series funding for new research center",
    ]

    for hl in headlines:
        score = lex.score_text(hl)
        print(f"  Headline: {hl}")
        print(f"  Sentiment: {score.label()} (pos={score.positive_count}, neg={score.negative_count}, neut={score.neutral_count})")
        print()
