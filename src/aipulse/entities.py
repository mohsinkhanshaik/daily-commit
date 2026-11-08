"""Company and model name extraction via a curated lexicon.

Fixes over the first version, all visible on the real archive:
- Canonical display names. Companies were printed with str.title(), which
  turned "openai" into "Openai" and "xai" into "Xai"; each entry now
  carries its proper spelling and the aliases that should map to it
  ("Google DeepMind", "DeepMind" -> Google).
- Longest match wins. "gpt-5" used to match inside "gpt-5.6", so one
  mention produced two models. Model patterns are tried longest first and
  the matched span is blanked out before shorter patterns run.
- Word boundaries everywhere, so "together" (Together AI) and "meta" no
  longer fire on ordinary English like "taken together" or "metadata".
- An up-to-date lexicon built from names that actually appear in digests/
  (GPT-6, Claude Fable, Kimi K3, Gemini 3.8, DeepSeek V4, Qwen 3.8, ...).
  Versioned families use a regex so new point releases are caught without
  editing the lexicon every week, and each family names its maker, so a
  story that only says "Kimi K3" still credits Moonshot AI.
"""

import re
from dataclasses import dataclass, field

COMPANIES = {
    "OpenAI": ["openai"],
    "Anthropic": ["anthropic"],
    "Google": ["google", "deepmind", "google deepmind", "alphabet"],
    "Meta": ["meta platforms", "meta ai", "meta's", "meta"],
    "xAI": ["xai"],
    "Microsoft": ["microsoft"],
    "Amazon": ["amazon", "aws"],
    "Apple": ["apple"],
    "Nvidia": ["nvidia"],
    "AMD": ["amd"],
    "Intel": ["intel"],
    "TSMC": ["tsmc"],
    "DeepSeek": ["deepseek"],
    "Moonshot AI": ["moonshot ai", "moonshot"],
    "Alibaba": ["alibaba"],
    "Mistral AI": ["mistral ai", "mistral"],
    "Together AI": ["together ai"],
    "SpaceX": ["spacex"],
    "Qualcomm": ["qualcomm"],
}
MODEL_FAMILIES = [
    ("OpenAI", r"gpt-\d+(?:\.\d+)?(?:[ -](?:turbo|mini|cyber|sol|terra|luna))?"),
    ("Anthropic", r"claude (?:fable|mythos|opus|sonnet|haiku)(?: \d+(?:\.\d+)?)?"),
    ("Google", r"gemini \d+(?:\.\d+)?(?: (?:pro|flash|ultra))?"),
    ("xAI", r"grok \d+(?:\.\d+)?"),
    ("Meta", r"llama \d+(?:\.\d+)?"),
    ("Moonshot AI", r"kimi k\d+(?:\.\d+)?"),
    ("DeepSeek", r"deepseek[ -][vr]\d+(?:\.\d+)?"),
    ("Alibaba", r"qwen ?\d+(?:\.\d+)?"),
    ("OpenAI", r"\bo[1-9](?:-mini|-pro)?"),
]
_COMPANY_RES = sorted(
    ((re.compile(r"\b" + re.escape(alias) + r"\b"), name)
     for name, aliases in COMPANIES.items() for alias in aliases),
    key=lambda pair: -len(pair[0].pattern))
_MODEL_RES = [(re.compile(r"(?<![\w.])" + pat + r"(?![\w])"), maker)
              for maker, pat in MODEL_FAMILIES]


@dataclass
class Entities:
    """Extracted company and model names from a news item."""
    companies: list = field(default_factory=list)
    models: list = field(default_factory=list)

    def all(self):
        return self.companies + self.models


def _pretty_model(raw):
    """'deepseek v4' -> 'DeepSeek V4', 'qwen3.8' -> 'Qwen 3.8', 'gpt-6' -> 'GPT-6'."""
    raw = re.sub(r"^(qwen)(\d)", r"\1 \2", raw).replace("deepseek-", "deepseek ")
    words = []
    for word in raw.split():
        if word.startswith("gpt-"):
            words.append("GPT-" + word[4:])
        elif word == "deepseek":
            words.append("DeepSeek")
        elif re.match(r"^[kvr]\d", word):
            words.append(word.upper())
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words)


def extract_entities(text: str) -> Entities:
    """Extract canonical company names and model names from text."""
    low = text.lower()
    companies, models = [], []
    for pattern, name in _COMPANY_RES:
        if name not in companies and pattern.search(low):
            companies.append(name)
    masked = low
    for pattern, maker in _MODEL_RES:
        for match in pattern.finditer(masked):
            name = _pretty_model(match.group(0))
            if name not in models:
                models.append(name)
            if maker not in companies:
                companies.append(maker)
        masked = pattern.sub(lambda m: " " * len(m.group(0)), masked)
    return Entities(companies=companies, models=models)


def annotate(item):
    """Fill item.entities (companies then models) from headline + summary."""
    item.entities = extract_entities(item.headline + " " + item.summary).all()
    return item


if __name__ == "__main__":
    sample = ("OpenAI released GPT-5.6 Sol last week while Google DeepMind shipped Gemini 3.8 Pro. "
              "Anthropic's Claude Fable 5 and Moonshot's Kimi K3 compete; DeepSeek V4 runs on Nvidia GPUs. "
              "Taken together, the metadata shows xAI pricing Grok 4.5 low.")
    found = extract_entities(sample)
    print("Companies:", found.companies)
    print("Models:   ", found.models)
