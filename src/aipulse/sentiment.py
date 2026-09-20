"""Lexicon-based sentiment analysis for news items.

This module provides sentiment scoring for NewsItem objects using positive
and negative word lexicons. Sentiment serves multiple purposes: tracking
emotional tone of coverage (neutral, positive, negative), understanding
whether a news story is bullish or bearish for stakeholders, and grouping
stories by sentiment for risk monitoring.
"""\nfrom enum import Enum\nfrom dataclasses import dataclass\n\nclass Sentiment(Enum):\n    POSITIVE = "positive"\n    NEGATIVE = "negative"\n    NEUTRAL = "neutral"\n\n@dataclass\nclass SentimentScore:\n    sentiment: Sentiment\n    confidence: float\n\nPOS_WORDS = {\n    "breakthrough", "surge", "soaring", "milestone", "bullish",\n    "upbeat", "positive", "strong", "gains", "outperform",\n    "accelerated", "growth", "expansion", "success", "opportunity",\n    "record", "beat", "exceed", "advance", "rise"\n}\n\nNEG_WORDS = {\n    "decline", "falls", "bearish", "downbeat", "negative",\n    "weak", "losses", "underperform", "slowed", "contraction",\n    "risk", "miss", "miss", "slide", "drop", "slump", "crash",\n    "plunge", "concern", "challenge", "headwind"\n}\n\ndef analyze(text: str) -> SentimentScore:\n    words = text.lower().split()\n    pos_count = sum(1 for w in words if w.strip(".,!?;:") in POS_WORDS)\n    neg_count = sum(1 for w in words if w.strip(".,!?;:") in NEG_WORDS)\n    total = pos_count + neg_count\n    if total == 0:\n        return SentimentScore(Sentiment.NEUTRAL, 0.0)\n    confidence = abs(pos_count - neg_count) / total\n    if pos_count > neg_count:\n        return SentimentScore(Sentiment.POSITIVE, confidence)\n    elif neg_count > pos_count:\n        return SentimentScore(Sentiment.NEGATIVE, confidence)\n    else:\n        return SentimentScore(Sentiment.NEUTRAL, 0.0)

if __name__ == "__main__":
    test_headlines = [
        "AI breakthrough promises strong gains in efficiency",
        "Tech sector decline raises market concerns",
        "Neutral market update on regulatory developments"
    ]
    for headline in test_headlines:
        score = analyze(headline)
        print(f"{headline} -> {score.sentiment.value} ({score.confidence:.2f})")
