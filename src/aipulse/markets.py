"""Stock and index move extraction for AI Pulse (day 49).

AI news now moves markets: export curbs, IPOs and chip order cuts show up
as percentage swings in Nvidia, Broadcom or the Nasdaq. This module scans
plain text (a NewsItem summary or any string) for sentences that pair a
known market name with a percentage, and returns signed MarketMove records.
Design: a small alias lexicon maps names to canonical labels, the nearest
name before each number wins, and direction comes from verbs in a short
window around the number. Regex plus stdlib only, so it runs on any digest.
"""

import re
from dataclasses import dataclass

LEXICON = {"nvidia": "Nvidia", "broadcom": "Broadcom", "mediatek": "MediaTek",
           "nasdaq": "Nasdaq 100", "taiex": "TAIEX", "s&p": "S&P 500",
           "anthropic": "Anthropic", "amd": "AMD", "tsmc": "TSMC"}
UP = re.compile(r"\b(rose|rise|gain|jump|climb|surge|rall|higher|above)")
DOWN = re.compile(r"\b(fell|fall|drop|down|lost|slid|slump|plunge|lower|below)")
PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent)")


@dataclass
class MarketMove:
    name: str
    percent: float
    sentence: str


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def nearest_name(sentence, index):
    best = None
    low = sentence.lower()
    for alias, canon in LEXICON.items():
        for m in re.finditer(r"\b" + re.escape(alias) + r"\b", low):
            if m.start() < index and (best is None or m.start() > best[0]):
                best = (m.start(), canon)
    return best[1] if best else None


def direction(window):
    low = window.lower()
    if DOWN.search(low):
        return -1
    return 1 if UP.search(low) else 0


def extract_moves(text):
    moves = []
    for sentence in split_sentences(text):
        for match in PCT.finditer(sentence):
            name = nearest_name(sentence, match.start())
            window = sentence[max(0, match.start() - 40):match.end() + 12]
            sign = direction(window)
            if name and sign:
                moves.append(MarketMove(name, sign * float(match.group(1)), sentence))
    return moves


def biggest_moves(moves, limit=3):
    return sorted(moves, key=lambda m: abs(m.percent), reverse=True)[:limit]


def average_by_name(moves):
    totals = {}
    for move in moves:
        totals.setdefault(move.name, []).append(move.percent)
    return {name: round(sum(v) / len(v), 2) for name, v in totals.items()}


if __name__ == "__main__":
    sample = ("The Nasdaq 100 fell 5.6% on Friday. Nvidia dropped 22.9% on the week. "
              "Broadcom fell 11.4% after a TPU order cut report. "
              "Anthropic shares closed about 17% above the offer price.")
    found = extract_moves(sample)
    for move in biggest_moves(found, 5):
        print("%-12s %+6.1f%%" % (move.name, move.percent))
    print(average_by_name(found))
