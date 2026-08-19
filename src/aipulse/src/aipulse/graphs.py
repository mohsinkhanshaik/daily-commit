"""ASCII trend charts for AI Pulse archive.

Generates simple terminal-friendly line and bar charts from term frequencies
and scoring data. Charts use Unicode box-drawing characters and scale to terminal
width. Each chart displays a title, axis labels, and data points as blocks.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass
class Point:
    """A single (x, y) coordinate for charting."""
    label: str
    value: float


class ASCIIChart:
    """ASCII bar and line chart renderer."""

    def __init__(self, width: int = 60, height: int = 12):
        self.width = width
        self.height = height

    def bar_chart(self, title: str, points: List[Point], max_val: float = None) -> str:
        """Render a horizontal bar chart."""
        if not points:
            return "(no data)"

        max_val = max_val or max(p.value for p in points)
        if max_val == 0:
            max_val = 1.0

        lines = [title]
        for pt in points:
            bar_len = int((pt.value / max_val) * (self.width - 20))
            bar = "█" * bar_len
            lines.append(f"{pt.label:15} | {bar} {pt.value:.1f}")
        return "\n".join(lines)

    def line_chart(self, title: str, points: List[Point], max_val: float = None) -> str:
        """Render a simple line chart using Unicode block characters."""
        if not points:
            return "(no data)"

        max_val = max_val or max(p.value for p in points)
        if max_val == 0:
            max_val = 1.0

        lines = [title]
        for row in range(self.height, 0, -1):
            threshold = (row / self.height) * max_val
            row_line = ""
            for pt in points:
                if pt.value >= threshold:
                    row_line += "█"
                else:
                    row_line += " "
            lines.append(row_line)

        labels = "  " + " ".join(p.label[:1] for p in points)
        lines.append(labels)
        return "\n".join(lines)


if __name__ == "__main__":
    chart = ASCIIChart(width=60, height=10)
    points = [
        Point("Models", 15),
        Point("Robots", 8),
        Point("Chips", 12),
        Point("Policy", 5),
    ]

    print(chart.bar_chart("AI News by Category", points))
    print()
    print(chart.line_chart("Trend Over Days", points[:3], max_val=20))
