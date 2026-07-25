"""Rule-based topic tagging for news items.

Assigns Category tags to NewsItems based on keyword patterns in headlines
and summaries. Rules prioritize in order: models > chips > funding > policy
> research > products > other.
"""

from enum import Enum
from aipulse.models import NewsItem, Category


CATEGORY_KEYWORDS = {
    Category.MODELS: {
        'keywords': ['model', 'gpt', 'claude', 'gemini', 'llm', 'release', 'launch', 'inference', 'parameter', 'token'],
        'phrases': ['frontier lab', 'model suite', 'new model']
    },
    Category.CHIPS: {
        'keywords': ['chip', 'gpu', 'nvidia', 'tensor', 'compute', 'hardware', 'gb300', 'h100', 'processor'],
        'phrases': ['ai chip', 'processing unit', 'colossus']
    },
    Category.FUNDING: {
        'keywords': ['funding', 'raise', 'series', 'million', 'billion', 'venture', 'invest', 'round', 'capital'],
        'phrases': ['funding round', 'venture capital', 'investment']
    },
    Category.POLICY: {
        'keywords': ['regulation', 'policy', 'export', 'control', 'government', 'law', 'rule', 'compliance'],
        'phrases': ['export control', 'federal', 'commerce department']
    },
    Category.RESEARCH: {
        'keywords': ['research', 'paper', 'benchmark', 'score', 'performance', 'technique', 'architecture'],
        'phrases': ['benchmark', 'sota', 'state-of-art']
    },
    Category.PRODUCTS: {
        'keywords': ['product', 'tool', 'feature', 'beta', 'release', 'available', 'app', 'service'],
        'phrases': ['product launch', 'now available', 'beta']
    },
}


def tag_item(item: NewsItem) -> Category:
    """Assign a primary category to a news item based on headline and summary."""
    text = (item.headline + ' ' + item.summary).lower()

    for category in [Category.MODELS, Category.CHIPS, Category.FUNDING,
                     Category.POLICY, Category.RESEARCH, Category.PRODUCTS]:
        rules = CATEGORY_KEYWORDS.get(category, {})

        for phrase in rules.get('phrases', []):
            if phrase.lower() in text:
                return category

        keywords = rules.get('keywords', [])
        if keywords and sum(1 for kw in keywords if kw.lower() in text) >= 2:
            return category

        if keywords and any(kw.lower() in text for kw in keywords[:3]):
            if category == Category.MODELS or category == Category.CHIPS:
                return category

    return Category.OTHER

def tag_batch(items: list[NewsItem]) -> list[NewsItem]:
    """Tag a list of news items in place, returning the list."""
    for item in items:
        item.category = tag_item(item)
    return items


if __name__ == '__main__':
    samples = [
        NewsItem('GPT-5.6 Released', 'OpenAI announced three new models in the GPT-5.6 family.'),
        NewsItem('Reflection AI Secures $6.3B Chip Deal', 'Reflection AI locked in a compute lease for Nvidia GB300 chips.'),
        NewsItem('New AI Policy Framework', 'US Commerce Department signals regulation on AI chip exports.'),
    ]

    tagged = tag_batch(samples)
    for item in tagged:
        print(f"{item.headline} -> {item.category.value}")
