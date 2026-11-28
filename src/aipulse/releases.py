"""Model release and version extraction for AI Pulse (day 50).

Most AI headlines are launches: a lab ships a model name with a version
number, often in tiers (GPT-6.2 Astra and Sol, DeepSeek-V4.1-Flash).
This module scans plain text for names that pair a known family with a
version, links each to the lab that makes it, and flags launch sentences.
Design: a family lexicon maps a name to its lab, one regex captures family,
version and an optional tier word, and a short verb list decides whether
the sentence announces a release. Stdlib only, so it runs on any digest.
"""

import re
from dataclasses import dataclass

FAMILIES = {"gpt": "OpenAI", "claude": "Anthropic", "gemini": "Google",
"llama": "Meta", "deepseek": "DeepSeek", "qwen": "Alibaba",
"grok": "xAI", "hy": "Tencent", "mistral": "Mistral"}
MODEL = re.compile(r"\b(GPT|Claude|Gemini|Llama|DeepSeek|Qwen|Grok|Hy|Mistral)"
r"[- ]?V?(\d+(?:\.\d+)?)(?:[- ]([A-Z][a-z]+))?")
LAUNCH = re.compile(r"\b(launch|release|ship|unveil|debut|open-sourc|introduc)", re.I)
STOP = {"The", "And", "On", "In", "At", "For", "With"}

@dataclass
class ModelMention:
    lab: str
    family: str
    version: str
    tier: str
    launch: bool

    def label(self):
        base = "%s-%s" % (self.family, self.version)
        return base + " " + self.tier if self.tier else base

def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def version_key(version):
    return tuple(int(part) for part in version.split("."))

def extract_models(text):
    found = []
    for sentence in split_sentences(text):
        is_launch = bool(LAUNCH.search(sentence))
        for m in MODEL.finditer(sentence):
            tier = "" if m.group(3) in STOP else (m.group(3) or "")
            lab = FAMILIES[m.group(1).lower()]
            found.append(ModelMention(lab, m.group(1), m.group(2), tier, is_launch))
    return found

def unique_models(mentions):
    seen = {}
    for item in mentions:
        if item.label() not in seen or item.launch:
            seen[item.label()] = item
    return list(seen.values())

def latest_by_lab(mentions):
    best = {}
    for item in mentions:
        current = best.get(item.lab)
        if current is None or version_key(item.version) > version_key(current.version):
            best[item.lab] = item
    return best

if __name__ == "__main__":
    sample = ("OpenAI launched GPT-6.2 Astra and GPT-6.2 Sol on Nov 17. "
              "Tencent says DFly2 lifts DeepSeek-V4.1-Flash throughput 81%. "
              "Hy4 Flash agent tasks ran 4.2x faster. "
              "An older GPT-5 note and a Claude 4 mention round it out.")
    mentions = extract_models(sample)
    for item in unique_models(mentions):
        print("%-10s %-22s launch=%s" % (item.lab, item.label(), item.launch))
    for lab, item in sorted(latest_by_lab(mentions).items()):
        print("latest", lab, item.label())
