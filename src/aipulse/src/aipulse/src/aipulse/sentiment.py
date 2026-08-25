"""Day 23: Lexicon-based tone scoring for news items.

Assigns sentiment scores to news content based on lexicon matching.
Supports positive, negative, neutral classification with confidence.
"""

from dataclasses import dataclass
from enum import Enum


class Sentiment(Enum):
    """Sentiment category."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentScore:
    """Sentiment analysis result."""
    sentiment: Sentiment
    confidence: float  # 0.0 to 1.0
    positive_count: int
    negative_count: int


class SentimentAnalyzer:
    """Lexicon-based sentiment scorer."""

    def __init__(self):
        self.positive_words = {
            "breakthrough", "advancement", "success", "growth", "surge",
            "innovation", "record", "powerful", "strong", "leading",
            "improved", "outperform", "pioneer", "massive", "investment",
        }
        self.negative_words = {
            "risk", "concern", "threat", "decline", "struggle",
            "failure", "weak", "danger", "cyberattack", "breach",
            "restrictions", "penalty", "issue", "challenge", "warning",
        }

    def score(self, text: str) -> SentimentScore:
        """Score sentiment of a text passage."""
        words = text.lower().split()
        pos_count = sum(1 for w in words if w.strip('.,!?;:') in self.positive_words)
        neg_count = sum(1 for w in words if w.strip('.,!?;:') in self.negative_words)
        total_matched = pos_count + neg_count

        if total_matched == 0:
            return SentimentScore(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0,
                positive_count=0,
                negative_count=0,
            )

        confidence = total_matched / max(len(words), 10)
        if pos_count > neg_count:
            sentiment = Sentiment.POSITIVE
        elif neg_count > pos_count:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL

        return SentimentScore(
            sentiment=sentiment,
            confidence=min(confidence, 1.0),
            positive_count=pos_count,
            negative_count=neg_count,
        )


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    test_texts = [
        "Major AI breakthrough in robotics with record investment.",
        "Cybersecurity risks from AI-powered cyberattacks emerging.",
        "New AI model released for general use.",
    ]
    for text in test_texts:
        result = analyzer.score(text)
        print(f"Text: {text}")
        print(f"  Sentiment: {result.sentiment.value}, Confidence: {result.confidence:.2f}")
        print()
