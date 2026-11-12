"""Security incident and breach extraction for AI Pulse (day 48).

AI news increasingly includes security failures: stolen keys, leaked
data, unauthorized model usage, and agents reaching systems they should
not. This module flags those stories and pulls out two numbers that make
incidents comparable: the dollar loss and the count of affected units.

Design: an item is an incident when its text contains any word from
INCIDENT_TERMS. The loss is the largest dollar figure in the text, since
loss amounts are usually the headline number. The exposure is the largest
plain count that sits right before a unit word such as accounts or
workspaces. Severity is a simple 1-3 scale built from those two numbers,
so callers can sort without a model; inputs are plain strings.
"""
import re
from dataclasses import dataclass

INCIDENT_TERMS = ("breach", "stole", "stolen", "leak", "leaked", "hack",
                  "unauthorized", "exposed", "compromised", "ransomware")
UNITS = ("accounts", "users", "workspaces", "customers", "records")
SCALE = {"": 1, "k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6,
         "b": 1e9, "billion": 1e9}
MONEY_RE = re.compile(r"\$(\d[\d,]*(?:\.\d+)?)\s*(thousand|million|billion|[kmb])?\b", re.I)
COUNT_RE = re.compile(r"(\d[\d,]*)\s+(?:\w+\s+)?(" + "|".join(UNITS) + r")\b", re.I)


@dataclass
class Incident:
    headline: str
    loss_usd: float
    exposed: int
    severity: int


def is_incident(text):
    low = text.lower()
    return any(re.search(r"\b" + t + r"\b", low) for t in INCIDENT_TERMS)


def largest_loss(text):
    values = [float(n.replace(",", "")) * SCALE[(u or "").lower()]
              for n, u in MONEY_RE.findall(text)]
    return max(values, default=0.0)


def largest_exposure(text):
    return max((int(n.replace(",", "")) for n, _ in COUNT_RE.findall(text)), default=0)


def severity(loss_usd, exposed):
    if loss_usd >= 10e6 or exposed >= 1_000_000:
        return 3
    if loss_usd >= 100e3 or exposed >= 10_000:
        return 2
    return 1


def extract(headline, summary=""):
    text = headline + " " + summary
    if not is_incident(text):
        return None
    loss, exposed = largest_loss(text), largest_exposure(text)
    return Incident(headline, loss, exposed, severity(loss, exposed))


def rank(stories):
    found = [extract(h, s) for h, s in stories]
    return sorted([i for i in found if i], key=lambda i: (-i.severity, -i.loss_usd))


if __name__ == "__main__":
    demo = [
        ("Railway breach leads to AI charges",
         "Attackers stole customer secrets, causing about $740,000 in "
         "unauthorized AI charges; up to 100,000 workspaces were exposed."),
        ("Mercor raises $750 million", "Series D at a $20 billion valuation."),
        ("Agent reaches Medicare portal",
         "An unauthorized agent session accessed a statistics portal."),
    ]
    for inc in rank(demo):
        print(inc.severity, inc.headline, int(inc.loss_usd), inc.exposed)
