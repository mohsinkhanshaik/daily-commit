"""Lexicon-based sentiment scoring for news items.

This module provides tone analysis using hand-crafted sentiment lexicons.
Scores NewsItem objects with positive, neutral, or negative sentiment based
on keyword presence and patterns in headlines and summaries.
"""

from enum import Enum
from models import NewsItem


class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NEGATIVE = 'negative'

POSITIVE_WORDS = {
    'breakthrough', 'success', 'achieve', 'leader', 'advance', 'excellent',
    'growth', 'surge', 'boom', 'record', 'soar', 'pioneering', 'innovative'
}

NEGATIVE_WORDS = {
    'crash', 'decline', 'fail', 'risk', 'challenge', 'outage', 'shortage',
    'delay', 'concern', 'restrict', 'ban', 'cutback', 'recession'
}

def score_item(item: NewsItem) -> Sentiment:
    \"\"\"Score a NewsItem's sentiment using lexicon matching.\"\"\"
    text = (item.headline + ' ' + item.summary).lower()
    pos_count = sum(1 for w in POSITIVE_WORDS if w in text)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text)
    if pos_count > neg_count:
        return Sentiment.POSITIVE
    elif neg_count > pos_count:
        return Sentiment.NEGATIVE
    return Sentiment.NEUTRAL


if __name__ == '__main__':
    from models import NewsItem, Category
    items = [
        NewsItem('Breakthrough AI breakthrough', 'Major advance in models', 'Tech', '', Category.RESEARCH),
        NewsItem('Chip shortage delay', 'Supply chain at risk', 'Chips', '', Category.OTHER),
        NewsItem('Standard update', 'Regular news item', 'News', '', Category.OTHER),
    ]
    for item in items:
        print(f'{item.headline}: {score_item(item).value}')
