"""Lexicon-based sentiment analysis for news items.

Provides rule-based sentiment scoring using positive and negative word patterns.
Designed for quick, interpretable sentiment classification without machine learning.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class SentimentScore:
    sentiment: Sentiment
    confidence: float
    positive_count: int
    negative_count: int
    text_length: int

class SentimentAnalyzer:
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'amazing', 'wonderful',
        'fantastic', 'positive', 'growth', 'success', 'advancement',
        'breakthrough', 'leading', 'innovative', 'strong', 'up'
    }
    NEGATIVE_WORDS = {
        'bad', 'poor', 'terrible', 'awful', 'horrible',
        'negative', 'decline', 'loss', 'risk', 'threat',
        'challenge', 'weak', 'down', 'problem', 'issue'
    }

    def analyze(self, text: str) -> SentimentScore:
        words = text.lower().split()
        positive = sum(1 for w in words if w.strip('.,!?;:') in self.POSITIVE_WORDS)
        negative = sum(1 for w in words if w.strip('.,!?;:') in self.NEGATIVE_WORDS)
        total = len(words)
        if positive > negative:
            sentiment = Sentiment.POSITIVE
            confidence = min(positive / max(total, 1), 1.0)
        elif negative > positive:
            sentiment = Sentiment.NEGATIVE
            confidence = min(negative / max(total, 1), 1.0)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.5

        return SentimentScore(
            sentiment=sentiment,
            confidence=confidence,
            positive_count=positive,
            negative_count=negative,
            text_length=total
        )

if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    test_cases = [
        'Great news on AI breakthrough with positive results',
        'Concerns about risks and challenges in deployment',
        'Neutral reporting on technical details'
    ]
    for text in test_cases:
        score = analyzer.analyze(text)
        print(f'{score.sentiment.value}: {score.confidence:.2f}')
