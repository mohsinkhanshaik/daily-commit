"""Policy event extraction for AI Pulse (day 45).

AI policy stories share one shape: a jurisdiction (who acts), an action
(which lever is pulled) and a headline (what it is about). This module
tags news text with those fields using two small lexicons and padded
substring matching, so every result is predictable and easy to audit.
JURISDICTIONS maps aliases to a canonical region; ACTIONS is an ordered
list, so a specific lever such as an injunction wins over generic words
like rules. policy_matrix counts jurisdiction/action pairs so weekly
reports can show where regulatory pressure is building. Stdlib only.
"""
from collections import Counter
from dataclasses import dataclass, field

JURISDICTIONS = {
    "us": [" doj ", "justice department", "congress", "senate", "white house", "federal"],
    "eu": [" eu ", "european commission", "ai act", "brussels"],
    "uk": [" uk ", " cma ", "ofcom", "britain"],
    "china": ["beijing", "china", "chinese"],
    "local": ["county", "city council", "voters", "ballot", "new york", "amsterdam"],
    "other": ["norway", "brazil", "india", "japan", "korea", "australia"],
}

ACTIONS = [
    ("lawsuit", [" sue ", " sues ", "lawsuit", "complaint"]),
    ("injunction", ["injunction", "court order"]),
    ("investigation", ["probe", "investigat", "oversight", "briefing"]),
    ("enforcement", ["task force", "charged", "prosecut", " fine "]),
    ("export_control", ["export", "chip ban"]),
    ("legislation", [" bill ", " act ", " law ", "measure"]),
    ("rulemaking", [" rule", "regulation", "framework", "guidance"]),
]

@dataclass
class PolicyEvent:
    headline: str
    jurisdictions: list = field(default_factory=list)
    action: str = "none"
    def is_policy(self):
        return self.action != "none" and bool(self.jurisdictions)

def _pad(text):
    return " " + text.lower().replace(",", " ").replace(".", " ") + " "

def find_jurisdictions(text):
    low = _pad(text)
    return sorted(k for k, aliases in JURISDICTIONS.items() if any(a in low for a in aliases))

def find_action(text):
    low = _pad(text)
    for name, cues in ACTIONS:
        if any(c in low for c in cues):
            return name
    return "none"

def extract_event(headline, summary=""):
    text = headline + " " + summary
    return PolicyEvent(headline, find_jurisdictions(text), find_action(text))

def policy_matrix(events):
    counts = Counter()
    for ev in events:
        if ev.is_policy():
            for j in ev.jurisdictions:
                counts[(j, ev.action)] += 1
    return counts

if __name__ == "__main__":
    stories = [
        ("DOJ launches Super Intelligence Task Force", "It will prosecute AI misuse."),
        ("Meta pauses scraping terms", "After a Norway injunction and a UK CMA probe."),
        ("Voters back data center limits", "Restrictions passed in 40 of 41 local measures."),
        ("Congress plans Nvidia export oversight", "Democrats target China chip sales."),
        ("Google plans $17B Wyoming campus", "Powered by a 702MW fuel cell plant."),
    ]
    events = [extract_event(h, s) for h, s in stories]
    for ev in events:
        print(ev.action.ljust(14), ",".join(ev.jurisdictions) or "-", "|", ev.headline)
    for (j, a), n in sorted(policy_matrix(events).items()):
        print("matrix:", j, a, n)
