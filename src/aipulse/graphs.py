"""ASCII trend charts for AI Pulse digest metrics.

Renders simple text-based line charts, bar charts, and sparklines
for visualizing news metrics and trends over time. All output fits
standard terminal widths (80-120 chars) without external libraries.
"""
from datetime import date
from dataclasses import dataclass


@dataclass
class Series:
      """A time series of (date, value) data points."""
      points: list

    def __post_init__(self):
              self.points = sorted(self.points, key=lambda p: p[0])

    def normalize(self, height=10):
              """Scale values to fit in height rows."""
              if not self.points:
                            return []
                        vals = [v for _, v in self.points]
        min_v, max_v = min(vals), max(vals)
        if max_v == min_v:
                      return [(d, height // 2) for d, _ in self.points]
                  scale = (height - 1) / (max_v - min_v)
        return [(d, int((v - min_v) * scale)) for d, v in self.points]


def line_chart(series, width=80, height=10, title=""):
      """Render a line chart in ASCII."""
    if not series.points:
              return ""
    norm = series.normalize(height)
    grid = [['.' for _ in range(width)] for _ in range(height)]
    step = max(1, len(norm) // (width - 2))
    for i, (_, y) in enumerate(norm[::step]):
              if i < width - 2:
                            grid[height - 1 - y][i + 1] = '*'
                    lines = [''.join(row) for row in grid]
    if title:
              lines = [title.center(width)] + lines
    return '\n'.join(lines)


def bar_chart(labels_vals, width=80, title=""):
      """Render a bar chart in ASCII."""
    if not labels_vals:
              return ""
    vals = [v for _, v in labels_vals]
    max_v = max(vals) if vals else 1
    max_label_len = max((len(str(l)) for l, _ in labels_vals), default=5)
    bar_width = max(10, width - max_label_len - 5)
    lines = [title.center(width)] if title else []
    for label, val in labels_vals:
              bar_len = int((val / max_v) * bar_width) if max_v > 0 else 0
        bar = '#' * bar_len + ' ' * (bar_width - bar_len)
        line = f"{str(label).rjust(max_label_len)} | {bar} {val}"
        lines.append(line)
    return '\n'.join(lines)


def sparkline(values, width=20):
      """Render a tiny sparkline (like: ▁▂▃▄▅▆▇█)."""
    if not values:
              return ""
    chars = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
              return ''.join([chars[4]] * min(width, len(values)))
    scale = 8 / (max_v - min_v)
    spark = ''.join([chars[int((v - min_v) * scale)] for v in values[:width]])
    return spark


if __name__ == "__main__":
      test_points = [(date(2026, 8, d), 10 + d * 2) for d in range(1, 15)]
    ts = Series(test_points)
    print(line_chart(ts, title="News Count Over Time"))
    print()
    print(bar_chart([("Research", 15), ("Funding", 22), ("Policy", 8), ("Products", 18)], title="Stories by Category"))
    print()
    vals = [10 + i*2 for i in range(14)]
    print("Sparkline:", sparkline(vals))
