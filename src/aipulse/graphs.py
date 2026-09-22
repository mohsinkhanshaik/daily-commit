"""ASCII trend chart rendering for time-series data.

Provides functions to render trend data as ASCII charts, showing
value changes over time periods. Supports line charts with multiple
series and configurable scaling.
"""

from dataclasses import dataclass
from typing import Sequence, Optional


@dataclass
class Point:
    """A time-series data point."""
    label: str
    value: float


def render_line_chart(
    data: dict[str, Sequence[Point]],
    width: int = 60,
    height: int = 10
) -> str:
    """Render multiple time series as ASCII line chart.

    Args:
        data: Dict mapping series names to sequences of Points
        width: Chart width in characters
        height: Chart height in characters

    Returns:
        ASCII chart as multi-line string
    """
    if not data or not any(data.values()):
        return "[No data]"

    # Find min/max values for scaling
    all_values = [p.value for points in data.values() for p in points]
    if not all_values:
        return "[No data]"

    min_val = min(all_values)
    max_val = max(all_values)
    range_val = max_val - min_val or 1

    lines = []
    for row in range(height, -1, -1):
        line = ""
        threshold = min_val + (row / height) * range_val

        for col in range(width):
            chars = []
            for name, points in data.items():
                if col < len(points):
                    if points[col].value >= threshold * 0.9:
                        chars.append("*")
            line += chars[0] if chars else "-"

        lines.append(f"{threshold:6.1f} |{line}")

    # Add x-axis
    lines.append("       +" + "-" * width)
    return "\n".join(lines)


def sparkline(values: Sequence[float]) -> str:
    """Generate single-line sparkline from values."""
    if not values:
        return ""

    symbols = " .,-~*:^+"
    min_v, max_v = min(values), max(values)
    range_v = max_v - min_v or 1

    return "".join(
        symbols[int((v - min_v) / range_v * (len(symbols) - 1))]
        for v in values
    )


if __name__ == "__main__":
    # Demo: render sample trend data
    sample = {
        "searches": [Point(f"day{i}", 100 + i*5 + (i%3)*10) for i in range(10)],
        "articles": [Point(f"day{i}", 50 + i*3) for i in range(10)],
    }
    print("Trend Chart:")
    print(render_line_chart(sample, width=20, height=8))
    print("\nSparkline:")
    print(sparkline([100, 110, 105, 115, 120, 125, 130, 135, 140]))
