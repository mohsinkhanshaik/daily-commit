"""Frontier model capability tracking and comparison.

Represents frontier AI models with their key characteristics (lab, release date,
parameters, architecture, access level, benchmark scores). Enables systematic
comparison of capabilities across different frontier model releases from various
labs, supporting downstream features that track model proliferation and analyze
capability trends.
"""
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

class Architecture(Enum):
    TRANSFORMER = "transformer"
    MOE = "mixture_of_experts"
    HYBRID = "hybrid"
    RECURRENT = "recurrent"

@dataclass
class FrontierModel:
    lab: str
    name: str
    release_date: date
    parameters: int
    architecture: Architecture
    access_level: str
    scores: dict = field(default_factory=dict)

def compare_by_score(models, metric='overall'):
    """Rank frontier models by a specific benchmark metric."""
    return sorted(
        models, key=lambda m: m.scores.get(metric, 0), reverse=True
    )

if __name__ == "__main__":
    models = [
        FrontierModel(
            lab="Anthropic", name="Claude Opus 5.5",
            release_date=date(2026, 9, 15),
            parameters=200_000_000_000,
            architecture=Architecture.TRANSFORMER,
            access_level="API",
            scores={"overall": 86.4}
        ),
        FrontierModel(
            lab="OpenAI", name="GPT-6 Astra",
            release_date=date(2026, 8, 1),
            parameters=500_000_000_000,
            architecture=Architecture.MOE,
            access_level="Waitlist",
            scores={"overall": 84.9}
        ),
    ]
    ranked = compare_by_score(models)
    for model in ranked:
        print(f"{model.name} ({model.lab}): {model.scores['overall']}")
