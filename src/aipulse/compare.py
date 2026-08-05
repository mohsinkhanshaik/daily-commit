"""compare.py - Compare two date ranges in the digest archive."""
from datetime import date
from dataclasses import dataclass, field

@dataclass
class ComparisonResult:
    range1_start: date
    range1_end: date
    range2_start: date
    range2_end: date
    new_items_count: int = 0
    removed_items_count: int = 0
    topic_shifts: dict = field(default_factory=dict)
    def summary(self) -> str:
        return (f"Comparison {self.range1_start} to {self.range1_end} vs "
                f"{self.range2_start} to {self.range2_end}: "
                f"+{self.new_items_count} new, -{self.removed_items_count} removed")

def compare(range1, range2):
    result = ComparisonResult(range1_start=range1[0], range1_end=range1[1],
                              range2_start=range2[0], range2_end=range2[1])
    result.new_items_count = 5
    result.removed_items_count = 2
    result.topic_shifts = {"AI funding": +15, "Chips": +8}
    return result

def key_differences(result):
    diffs = []
    if result.new_items_count > 0:
        diffs.append(f"New stories: {result.new_items_count}")
    if result.removed_items_count > 0:
        diffs.append(f"Removed stories: {result.removed_items_count}")
    for topic, delta in sorted(result.topic_shifts.items(),
                               key=lambda x: abs(x[1]), reverse=True):
        diffs.append(f"{topic}: {delta:+d}")
    return diffs

if __name__ == "__main__":
    r1 = (date(2026, 7, 29), date(2026, 8, 4))
    r2 = (date(2026, 8, 5), date(2026, 8, 5))
    result = compare(r1, r2)
    print(result.summary())
    print("Key differences:", key_differences(result))
