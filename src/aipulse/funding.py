"""Funding round extraction and aggregation for AI Pulse (day 44).

Digest summaries mention money constantly: "$200M Series A+", "a $2.9
billion deal". This module turns that prose into structured FundingEvent
records so later tools can rank the week's biggest rounds or total the
capital flowing into a category.

Design: one regular expression finds amounts with an optional unit
(K, M, B, million, billion), a second finds round labels such as
"Series C" or "seed". Amounts are normalised to millions of US dollars,
so 2.9B becomes 2900.0. Extraction is pure; aggregation is a dict fold.
Only the largest amount in a text is kept, as headlines lead with it.
"""
import re
from dataclasses import dataclass

AMOUNT_RE = re.compile(r"\$\s?(\d+(?:\.\d+)?)\s?(billion|million|thousand|[BMK])?\b", re.I)
ROUND_RE = re.compile(r"\b(pre-seed|seed|series [a-h]\+?|ipo|acquisition|acquire[sd]?)\b", re.I)
UNIT_TO_MILLIONS = {"b": 1000.0, "billion": 1000.0, "m": 1.0, "million": 1.0,
                    "k": 0.001, "thousand": 0.001, "": 1e-6}


@dataclass
class FundingEvent:
    company: str
    amount_musd: float
    round_label: str = "unknown"


def parse_amount(number, unit):
    """Convert a matched number and unit into millions of USD."""
    return float(number) * UNIT_TO_MILLIONS[(unit or "").lower()]


def extract_amounts(text):
    """Return every dollar amount in text, in millions, in order seen."""
    return [parse_amount(n, u) for n, u in AMOUNT_RE.findall(text)]


def extract_round(text):
    """Return the first round label found, normalised to lower case."""
    match = ROUND_RE.search(text)
    if not match:
        return "unknown"
    label = match.group(1).lower()
    return "acquisition" if label.startswith("acquir") else label


def extract_event(company, text):
    """Build a FundingEvent from the largest amount in text, or None."""
    amounts = extract_amounts(text)
    if not amounts:
        return None
    return FundingEvent(company, max(amounts), extract_round(text))


def total_by_round(events):
    """Sum amounts per round label."""
    totals = {}
    for event in events:
        totals[event.round_label] = totals.get(event.round_label, 0.0) + event.amount_musd
    return totals


def top_events(events, n=3):
    """Return the n largest events, biggest first."""
    return sorted(events, key=lambda e: e.amount_musd, reverse=True)[:n]


if __name__ == "__main__":
    samples = [
        ("Sand.ai", "Sand.ai raised $200M in a Series A+ for video models."),
        ("Sentra", "Sentra closed a $150 million Series C led by Capital One."),
        ("Taalas", "AMD agreed to acquire Taalas for about $2.9B, $1.4B contingent."),
        ("Pliant", "Pliant raised $80M Series C for agent-ready payments."),
        ("NoMoney", "A lab published a new reasoning benchmark."),
    ]
    events = [e for e in (extract_event(c, t) for c, t in samples) if e]
    for event in top_events(events):
        print(f"{event.company:10} {event.amount_musd:>8.1f}M  {event.round_label}")
    print(total_by_round(events))
