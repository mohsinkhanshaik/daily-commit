"""Lexicon-based tone scoring for news items.

The original module did not import: from score_item onward the source had
been saved with escaped quotes (\\"\\"\\"), a SyntaxError. Fixing only the
quotes would have revived a scorer with three accuracy bugs, fixed here:

- Substring matching. 'ban' fired inside 'urban' and 'bank', 'risk'
  inside 'brisk', 'win' inside 'window'. Tokens are now whole words,
  and each lexicon word expands to its inflections (surge -> surges,
  surged, surging; ban -> bans, banned) so real usage still counts.
- No negation. "not a breakthrough" scored positive. A negator within the
  three preceding tokens flips the polarity of a hit.
- Presence, not counts. Each word counted at most once per item and the
  label had no strength. score_text() returns a value in [-1, 1]
  ((pos - neg) / (pos + neg)) and the label uses a +-0.2 dead zone so a
  single weak word in a long story stays NEUTRAL.
"""

import re
from enum import Enum

from models import NewsItem


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


POSITIVE_WORDS = ("breakthrough", "success", "succeed", "achieve", "lead", "leader", "advance",
                  "excellent", "growth", "grow", "surge", "boom", "record", "soar", "pioneer",
                  "innovate", "innovative", "beat", "outperform", "win", "gain", "expand",
                  "approve", "rally", "jump")
NEGATIVE_WORDS = ("crash", "decline", "fail", "failure", "risk", "challenge", "outage",
                  "shortage", "delay", "concern", "restrict", "ban", "cutback", "recession",
                  "lawsuit", "sue", "fraud", "layoff", "rout", "plunge", "slump", "probe",
                  "breach", "exploit", "halt", "warn", "loss", "lose", "erase", "fall", "fell")
NEGATORS = {"not", "no", "never", "without", "isnt", "wasnt", "arent"}
DEAD_ZONE = 0.2
_TOKEN = re.compile(r"[a-z]+")


def _forms(word):
    """Inflections of a base word: surge -> surges, surged, surging."""
    stem = word[:-1] if word.endswith("e") else word
    forms = {word, word + "s", word + "es", word + "d", word + "ed", stem + "ing", stem + "ed"}
    if len(word) <= 4 and word[-1] not in "aeiouwy" and word[-2] in "aeiou":
        forms |= {word + word[-1] + "ed", word + word[-1] + "ing"}  # ban -> banned
    return forms


POSITIVE_FORMS = set().union(*(_forms(w) for w in POSITIVE_WORDS))
NEGATIVE_FORMS = set().union(*(_forms(w) for w in NEGATIVE_WORDS))


def _polarity(token):
    if token in POSITIVE_FORMS:
        return 1
    if token in NEGATIVE_FORMS:
        return -1
    return 0


def score_text(text: str) -> float:
    """Tone in [-1, 1]; 0.0 when no lexicon word appears."""
    tokens = _TOKEN.findall(text.lower().replace("'", ""))
    pos = neg = 0
    for i, token in enumerate(tokens):
        polarity = _polarity(token)
        if polarity and NEGATORS.intersection(tokens[max(0, i - 3):i]):
            polarity = -polarity
        pos += polarity > 0
        neg += polarity < 0
    return 0.0 if pos + neg == 0 else (pos - neg) / (pos + neg)


def label(value: float) -> Sentiment:
    if value > DEAD_ZONE:
        return Sentiment.POSITIVE
    if value < -DEAD_ZONE:
        return Sentiment.NEGATIVE
    return Sentiment.NEUTRAL


def score_item(item: NewsItem) -> Sentiment:
    """Label a NewsItem's tone from its headline and summary."""
    return label(score_text(item.headline + " " + item.summary))


if __name__ == "__main__":
    items = [
        NewsItem("Nvidia surges to a record", "Chip sales soared on data center growth."),
        NewsItem("AI-chip rout erases 2.3 trillion dollars", "Nvidia plunged as investors fled."),
        NewsItem("Urban bank opens branch", "Nothing notable happened."),
        NewsItem("Lab says result is not a breakthrough", "Researchers warn of risk."),
    ]
    for it in items:
        print("%-42s %+.2f %s" % (it.headline, score_text(it.headline + " " + it.summary),
                                  score_item(it).value))
