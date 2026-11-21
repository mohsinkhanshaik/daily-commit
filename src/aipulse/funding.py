"""Funding round extraction and aggregation for AI Pulse (day 44).

Digests mention deals in prose; this module builds FundingEvent records.
Design: every amount is normalised to millions of USD by parse_amount, so
"$1.2B" and "$1,200 million" compare equal. One text often holds several
figures (round size, valuation, earlier raise). extract_event keeps the
largest figure that is NOT tagged as a valuation, because a valuation is
not money raised. Round labels come from a small ordered regex list, so a
specific "Series C" wins over the generic seed or acquisition patterns.
"""

import re
from dataclasses import dataclass

UNITS = {"k": 0.001, "thousand": 0.001, "m": 1.0, "million": 1.0,
         "b": 1000.0, "bn": 1000.0, "billion": 1000.0}
AMOUNT_RE = re.compile(
    r"(?:US)?\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)\s?(billion|million|thousand|bn|b|m|k)\b(\s+valuation)?",
    re.IGNORECASE)
ROUND_PATTERNS = [
    ("series", re.compile(r"\bseries\s+([a-h])\b", re.IGNORECASE)),
    ("seed", re.compile(r"\bpre-seed|\bseed\b", re.IGNORECASE)),
    ("convertible", re.compile(r"\bconvertible note", re.IGNORECASE)),
    ("acquisition", re.compile(r"\bacqui(?:res|red|sition)\b", re.IGNORECASE)),
]

@dataclass
class FundingEvent:
    company: str
    amount_musd: float
    round_label: str = "unknown"

def parse_amount(number, unit):
    """Convert '1,200' plus 'million' into 1200.0 millions of USD."""
    value = float(number.replace(",", ""))
    return round(value * UNITS[unit.lower()], 3)

def extract_amounts(text):
    """Return (amount_musd, is_valuation) pairs in order of appearance."""
    found = []
    for m in AMOUNT_RE.finditer(text):
        before = text[max(0, m.start() - 12):m.start()].lower()
        is_val = bool(m.group(3)) or "valued at" in before
        found.append((parse_amount(m.group(1), m.group(2)), is_val))
    return found

def extract_round(text):
    """Return the first matching round label, e.g. 'series c' or 'seed'."""
    for label, pattern in ROUND_PATTERNS:
        m = pattern.search(text)
        if m:
            return label + " " + m.group(1).lower() if m.groups() else label
    return "unknown"

def extract_event(company, text):
    raised = [amount for amount, is_val in extract_amounts(text) if not is_val]
    if not raised:
        return None
    return FundingEvent(company, max(raised), extract_round(text))

def total_by_round(events):
    totals = {}
    for event in events:
        totals[event.round_label] = totals.get(event.round_label, 0.0) + event.amount_musd
    return totals

def top_events(events, n=3):
    return sorted(events, key=lambda e: e.amount_musd, reverse=True)[:n]

if __name__ == "__main__":
    samples = [
        ("Future Secure AI", "Raised US$80 million in convertible notes at a US$1.2 billion valuation."),
        ("altM", "The startup raised $10.3 million, per an Indian funding roundup."),
        ("Demo Labs", "A $250K pre-seed round, later a $1,500 million Series C."),
    ]
    events = [e for e in (extract_event(c, t) for c, t in samples) if e]
    for event in top_events(events, 5):
        print(f"{event.company:18} {event.amount_musd:10.3f} M  {event.round_label}")
    print("Totals by round:", total_by_round(events))
