"""Compute and power deal extraction for AI Pulse (day 46).

Infrastructure stories now dominate the digest: data center campuses,
fuel cell contracts and chip supply deals. They carry the same hard
numbers - power (MW or GW), money ($ with a T, B or M suffix) and
sometimes accelerator counts. This module pulls those numbers out of
plain text with small regexes and normalizes them, so power is always
megawatts and money is always millions of US dollars. A ComputeDeal
keeps the headline next to its numbers, and capacity_by_entity sums
megawatts per company from a lexicon passed in by the caller, which
keeps it independent of entities.py. Stdlib only.
"""
import re
from collections import Counter
from dataclasses import dataclass

POWER_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(gw|mw)\b", re.I)
MONEY_RE = re.compile(r"\$(\d+(?:\.\d+)?)\s*(t|b|m)\b", re.I)
GPU_RE = re.compile(r"(\d[\d,]*)\s+(?:gpus|accelerators|chips)\b", re.I)
MONEY_SCALE = {"t": 1000000.0, "b": 1000.0, "m": 1.0}


@dataclass
class ComputeDeal:
    headline: str
    megawatts: float = 0.0
    usd_millions: float = 0.0
    gpus: int = 0

    def is_compute(self):
        return self.megawatts > 0 or self.gpus > 0


def parse_power(text):
    total = 0.0
    for value, unit in POWER_RE.findall(text):
        scale = 1000.0 if unit.lower() == "gw" else 1.0
        total += float(value) * scale
    return total


def parse_money(text):
    found = MONEY_RE.findall(text)
    if not found:
        return 0.0
    return max(float(v) * MONEY_SCALE[u.lower()] for v, u in found)


def parse_gpus(text):
    counts = [int(n.replace(",", "")) for n in GPU_RE.findall(text)]
    return max(counts) if counts else 0


def extract_deal(headline, summary=""):
    text = headline + " " + summary
    return ComputeDeal(headline, parse_power(text), parse_money(text), parse_gpus(text))


def capacity_by_entity(deals, lexicon):
    totals = Counter()
    for deal in deals:
        low = deal.headline.lower()
        for name in lexicon:
            if name.lower() in low:
                totals[name] += deal.megawatts
    return totals


if __name__ == "__main__":
    stories = [
        ("SpaceXAI files for Arizona campus", "Up to 6GW on 747 acres."),
        ("NTT signs Bloom fuel cell deal", "900 MW of onsite power from 2027."),
        ("Google buys Crusoe Wyoming site", "It plans to invest $17B there."),
        ("OpenAI closes first tranche", "$11B raised at a $1.25T valuation."),
    ]
    deals = [extract_deal(h, s) for h, s in stories]
    for d in deals:
        print(str(d.megawatts).rjust(8), "MW", str(d.usd_millions).rjust(10), "$M |", d.headline)
    print(capacity_by_entity(deals, ["SpaceXAI", "NTT", "Google"]).most_common())
