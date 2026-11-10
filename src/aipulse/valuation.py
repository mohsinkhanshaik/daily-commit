"""Valuation and IPO round tracking for AI Pulse (day 47).

Recent digests keep repeating one pattern: a headline valuation is
reported, then revised. OpenAI closed at $1.25T after seeking $1.4T,
and Anthropic IPO talk moved from $2T to $1.5T to a $1.2T-$1.3T range.
This module turns those headlines into ValuationMark records (company,
valuation in billions of US dollars, report date, and kind: round, ipo
or secondary) and orders them per company so each revision becomes a
number. step_changes returns the percent change between consecutive
marks, so a negative value is a down-round or a cut IPO target.
The valuation is taken as the largest dollar figure in a text that
mentions a valuation or an IPO, because the raise ($11B) is almost
always smaller than the price ($1.25T). Ranges use their midpoint.
Companies are matched with a lexicon passed in by the caller, the same
approach compute.py uses, so the module stays independent of
entities.py. Stdlib only.
"""
import re
from dataclasses import dataclass
from datetime import date

AMOUNT_RE = re.compile(r"\$(\d+(?:\.\d+)?)[tb]?(?:-\$?(\d+(?:\.\d+)?))?([tb])\b", re.I)
SCALE = {"t": 1000.0, "b": 1.0}
KIND_WORDS = [("ipo", "ipo"), ("listing", "ipo"), ("tender", "secondary"), ("secondary", "secondary")]

@dataclass
class ValuationMark:
    company: str
    billions: float
    day: date
    kind: str = "round"

def parse_amounts(text):
    values = []
    for low, high, unit in AMOUNT_RE.findall(text):
        mid = float(low) if not high else (float(low) + float(high)) / 2
        values.append(mid * SCALE[unit.lower()])
    return values

def classify(text):
    low = text.lower()
    for word, kind in KIND_WORDS:
        if word in low:
            return kind
    return "round"

def extract_mark(text, day, lexicon):
    low = text.lower()
    if "valu" not in low and "ipo" not in low:
        return None
    amounts = parse_amounts(text)
    company = next((n for n in lexicon if n.lower() in low), None)
    if not amounts or company is None:
        return None
    return ValuationMark(company, max(amounts), day, classify(text))

def step_changes(marks, company):
    own = sorted((m for m in marks if m.company == company), key=lambda m: m.day)
    changes = []
    for prev, cur in zip(own, own[1:]):
        pct = (cur.billions - prev.billions) / prev.billions * 100
        changes.append((cur.day.isoformat(), round(pct, 1)))
    return changes

def latest_by_company(marks):
    latest = {}
    for m in sorted(marks, key=lambda m: m.day):
        latest[m.company] = m
    return latest

if __name__ == "__main__":
    lexicon = ["OpenAI", "Anthropic"]
    reports = [
        (date(2026, 8, 20), "Anthropic IPO talk floats a $2T valuation"),
        (date(2026, 11, 1), "Anthropic IPO target discussed near a $1.5T valuation"),
        (date(2026, 11, 7), "Anthropic IPO now seen at a $1.2T-$1.3T valuation"),
        (date(2026, 10, 15), "OpenAI seeks a new round at a $1.4T valuation"),
        (date(2026, 11, 7), "OpenAI raises $11B at a $1.25T valuation"),
    ]
    marks = [extract_mark(text, day, lexicon) for day, text in reports]
    marks = [m for m in marks if m is not None]
    for name in lexicon:
        print(name.ljust(10), step_changes(marks, name))
    for name, m in latest_by_company(marks).items():
        print(name.ljust(10), m.kind.ljust(6), m.billions, "B on", m.day.isoformat())
