"""Lexicon-based sentiment analysis for news items.

Design: Simple keyword lexicon approach without ML dependencies.
Positive: growth, surge, boom, rise, strong, record, beat, leadership.
Negative: decline, crash, loss, risk, threat, concern, warning, slump.
Neutral: default for unknown or mixed-signal text. Handles edge cases gracefully.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict

class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

POSITIVE_WORDS = {
    'growth', 'surge', 'boom', 'rise', 'strong', 'record', 'beat',
    'leadership', 'advance', 'gain', 'jump', 'expand', 'win'
}

NEGATIVE_WORDS = {
    'decline', 'crash', 'loss', 'risk', 'threat', 'concern', 'warning',
    'slump', 'fall', 'drop', 'cut', 'worry', 'fail', 'challenge'
}

def score_text(text: str) -> Sentiment:
    """Score text sentiment using lexicon matching.

    Returns POSITIVE if positive words outnumber negative,
    NEGATIVE if negative words outnumber positive, else NEUTRAL.
    """
    if not text or not text.strip():
        return Sentiment.NEUTRAL

    words = text.lower().split()
    pos_count = sum(1 for w in words if w.strip('.,!?;:') in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w.strip('.,!?;:') in NEGATIVE_WORDS)

    if pos_count > neg_count:
        return Sentiment.POSITIVE
    elif neg_count > pos_count:
        return Sentiment.NEGATIVE
    else:
        return Sentiment.NEUTRAL

def summarize_sentiment(items: List) -> Dict:
    """Count sentiment distribution across items."""
    counts = {Sentiment.POSITIVE: 0, Sentiment.NEGATIVE: 0, Sentiment.NEUTRAL: 0}
    for item in items:
        if hasattr(item, 'sentiment'):
            counts[item.sentiment] += 1
    return counts

if __name__ == "__main__":
    @dataclass
    class NewsItem:
        headline: str
        summary: str
        sentiment: Sentiment = Sentiment.NEUTRAL

    items = [
        NewsItem("Growth surge in AI", "Market boom drives expansion"),
        NewsItem("Risk decline in systems", "Threat assessment drops"),
        NewsItem("Neutral tech news", "Standard development continues"),
    ]

    for item in items:
        item.sentiment = score_text(item.headline + " " + item.summary)

    dist = summarize_sentiment(items)
    print("Sentiment distribution:", dist)
    for item in items:
        print(f"  {item.headline}: {item.sentiment.value}")
