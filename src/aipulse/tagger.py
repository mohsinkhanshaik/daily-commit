"""tagger.py - Rule-based topic tagging for news items.

Applies a lexicon-based classifier to NewsItem objects to assign topic tags:
research, chips, funding, policy, companies, models, safety, infrastructure,
products. Rules key on headline keywords and summary patterns. No ML logic.
"""

from enum import Enum

class Tag(Enum):
    RESEARCH = "research"
    CHIPS = "chips"
    FUNDING = "funding"
    POLICY = "policy"
    COMPANIES = "companies"
    MODELS = "models"
    SAFETY = "safety"
    INFRASTRUCTURE = "infrastructure"
    PRODUCTS = "products"

def tag_item(headline, summary):
    """Apply rule-based classifier to a news item."""
    text = (headline + " " + summary).lower()
    tags = []

    if any(w in text for w in ["model", "gpt", "claude", "llm"]):
        tags.append(Tag.MODELS.value)
    if any(w in text for w in ["chip", "gpu", "nvidia", "semiconductor"]):
        tags.append(Tag.CHIPS.value)
    if any(w in text for w in ["fund", "raise", "invest", "million", "billion"]):
        tags.append(Tag.FUNDING.value)
    if any(w in text for w in ["policy", "regulation", "ftc", "governance"]):
        tags.append(Tag.POLICY.value)
    if any(w in text for w in ["safety", "risk", "security", "evaluation"]):
        tags.append(Tag.SAFETY.value)
    if any(w in text for w in ["infrastructure", "compute", "data center"]):
        tags.append(Tag.INFRASTRUCTURE.value)
    if any(w in text for w in ["anthropic", "openai", "meta", "google"]):
        tags.append(Tag.COMPANIES.value)
    if any(w in text for w in ["product", "launch", "announce"]):
        tags.append(Tag.PRODUCTS.value)

    return list(set(tags)) if tags else [Tag.RESEARCH.value]

if __name__ == "__main__":
    sample_headline = "OpenAI Raises GPT-5 with New Chip Infrastructure"
    sample_summary = "New model targets reasoning and coding at lower cost."
    tags = tag_item(sample_headline, sample_summary)
    print(f"Headline: {sample_headline}")
    print(f"Tags: {tags}")
