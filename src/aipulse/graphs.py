"""ASCII trend charts for terminal display.

Generates sparkline-style trend visualizations of term frequency and topic
momentum over time, suitable for embedding in terminal dashboards and reports.
"""

from dataclasses import dataclass
from typing import Sequence
from collections import Counter
import math


@dataclass
class Series:
    """Time series data point: timestamp and value."""
    day: str
    value: float


class Sparkline:
    """Convert numeric series to ASCII sparkline, 10 chars wide."""
    TICKS = ' ▁▂▃▄▅▆▇█'

    def __init__(self, points: Sequence[float]):
        if not points:
            self.spark = ' ' * 10
            return
        mn, mx = min(points), max(points)
        rng = mx - mn or 1
        normalized = [(p - mn) / rng for p in points]
        indices = [min(8, int(n * 8.5)) for n in normalized]
        self.spark = ''.join(self.TICKS[i] for i in indices[-10:])

    def render(self) -> str:
        return self.spark.rjust(10)


class BarChart:
    """Horizontal bar chart, 40 chars wide."""

    def __init__(self, labels: Sequence[str], values: Sequence[int]):
        mx = max(values) if values else 1
        self.bars = []
        for label, val in zip(labels, values):
            width = max(1, int(val / mx * 39))
            bar = '#' * width
            self.bars.append(f"{label:12} | {bar} {val}")

    def render(self) -> str:
        return '\n'.join(self.bars)


if __name__ == "__main__":
    # Demo: trend over 10 days
    trend_data = [42, 51, 38, 65, 72, 68, 81, 76, 88, 94]
    spark = Sparkline(trend_data)
    print(f"Trend chart: {spark.render()}")

    # Demo: top topics bar chart
    chart = BarChart(['AI Safety', 'Chips', 'Funding', 'Policy'], [15, 12, 9, 7])
    print("\nTop topics:")
    print(chart.render())
