"""Rule-based topic tagging for news items.

Each Category has a list of cues. A cue is matched as a whole word or
phrase (regex word boundaries, optional plural "s"), never as a raw
substring: the old tagger matched 'rule' inside 'ruled', 'token' inside
'tokenizer', 'app' inside 'apple' and 'ban' inside 'urban', which is why
so many stories landed in the wrong bucket.

Scoring: headline hits count double (headlines are written to state the
topic), summary hits count once, and the category with the highest score
wins. Ties fall back to PRIORITY order, so a GPU export-control story with
equal chips and policy evidence is tagged policy, the more specific lens.
A story needs a score of at least 2 to leave OTHER, so one stray word in
a long summary does not decide its category.

The old tagger also listed 'release' under both MODELS and PRODUCTS and
returned the first category with any two keywords, so ordering, not
evidence, decided most results.
"""

import re

from models import Category, NewsItem

CUES = {
    Category.MODELS: ["model", "llm", "gpt", "claude", "gemini", "grok", "llama",
                      "kimi", "qwen", "deepseek", "mistral", "open weights",
                      "frontier model", "reasoning model", "parameters", "context window"],
    Category.CHIPS: ["chip", "gpu", "nvidia", "amd", "tpu", "semiconductor", "foundry",
                     "tsmc", "hbm", "blackwell", "rubin", "h100", "h200", "gb300",
                     "data center", "datacenter", "compute", "wafer"],
    Category.FUNDING: ["funding", "raises", "raised", "series a", "series b", "series c",
                       "valuation", "ipo", "investors", "venture", "acquisition",
                       "acquires", "round", "seed"],
    Category.POLICY: ["regulation", "regulator", "policy", "law", "bill", "act",
                      "export controls", "ban", "lawsuit", "court", "antitrust",
                      "doj", "ftc", "commission", "congress", "senate", "executive order",
                      "compliance", "government"],
    Category.RESEARCH: ["research", "paper", "benchmark", "study", "arxiv", "dataset",
                        "researchers", "technique", "interpretability", "evaluation"],
    Category.PRODUCTS: ["launches", "launched", "app", "feature", "available",
                        "rollout", "subscription", "pricing", "api", "agent", "plugin"],
}
PRIORITY = [Category.POLICY, Category.FUNDING, Category.CHIPS, Category.RESEARCH,
            Category.MODELS, Category.PRODUCTS]
MIN_SCORE = 2
_PATTERNS = {cat: [re.compile(r"\b" + re.escape(cue) + r"s?\b") for cue in cues]
             for cat, cues in CUES.items()}


def score_categories(item: NewsItem) -> dict:
    """Return {Category: score}; headline hits weigh 2, summary hits 1."""
    head, body = item.headline.lower(), item.summary.lower()
    scores = {}
    for category, patterns in _PATTERNS.items():
        score = sum(2 for p in patterns if p.search(head))
        score += sum(1 for p in patterns if p.search(body))
        if score:
            scores[category] = score
    return scores


def tag_item(item: NewsItem) -> Category:
    """Return the best Category for an item (OTHER when evidence is thin)."""
    scores = score_categories(item)
    if not scores or max(scores.values()) < MIN_SCORE:
        return Category.OTHER
    best = max(scores.values())
    return next(c for c in PRIORITY if scores.get(c) == best)


def tag_batch(items: list) -> list:
    """Tag a list of news items in place, returning the list."""
    for item in items:
        item.category = tag_item(item)
    return items


if __name__ == "__main__":
    samples = [
        NewsItem("GPT-5.6 Released", "OpenAI announced three new models in the GPT-5.6 family."),
        NewsItem("Reflection AI Secures $6.3B Chip Deal", "A compute lease for Nvidia GB300 chips."),
        NewsItem("New AI Policy Framework", "US Commerce Department weighs export controls on AI chips."),
        NewsItem("Urban planners ruled on parking", "Nothing to do with AI at all."),
    ]
    for item in tag_batch(samples):
        print("%-40s -> %s" % (item.headline, item.category.value))
