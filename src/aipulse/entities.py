"""Entity extraction from AI industry news.

Identifies company and model names from news summaries using a curated
lexicon of major AI labs and their products. Supports case-insensitive
matching to handle variations in text formatting.

Future: Lexicon will be auto-generated from digest archives, tracking
company mentions and model releases over time.
"""

import re
from dataclasses import dataclass, field

# Curated lexicon of AI companies and model names.
LEXICON = {
    "openai": ["gpt-5.6", "gpt-5", "gpt-4"],
    "anthropic": ["claude 3.5", "claude 3"],
    "meta": ["llama 4", "llama 3"],
    "google": ["gemini 2", "gemini 1"],
    "xai": ["grok 4.5", "grok"],
    "spacex": ["starship"],
    "moonshot": ["kimi k3", "kimi"],
    "together": ["llama"],
    "nvidia": ["h200", "h100"],
}

@dataclass
class Entities:
    """Extracted company and model names from a news item."""
    companies: list = field(default_factory=list)
    models: list = field(default_factory=list)

def extract_entities(summary: str) -> Entities:
    """Extract company and model names from a news summary.

    Args:
        summary: Text to search for entity mentions.

    Returns:
        Entities object with matched companies and models.
    """
    companies = []
    models = []
    text_lower = summary.lower()
    for company, model_list in LEXICON.items():
        if re.search(r'\b' + re.escape(company) + r'\b', text_lower):
            companies.append(company.title())
        for model in model_list:
            if model.lower() in text_lower:
                models.append(model)
    return Entities(companies=list(set(companies)), models=list(set(models)))

if __name__ == "__main__":
    sample = "OpenAI released GPT-5.6 last week. Anthropic Claude 3.5 competes on inference cost."
    entities = extract_entities(sample)
    print(f"Companies: {entities.companies}")
    print(f"Models: {entities.models}")
