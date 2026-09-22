"""ASCII trend charts for time-series visualization in plaintext contexts.

Renders horizontal sparkline charts from date-value tuples, suitable for
terminal output and digest summaries. Supports rolling averages, peak/trough
detection, and axis labeling for term frequency and entity activity trends.
"""

from datetime import date, timedelta
from statistics import mean

SPARKLINE = " ▁▂▃▄▅▆▇█"

class TrendChart:
    """Render ASCII trend charts from time-series data."""

    def __init__(self, data, width=40, label=""):
        """data: list of (date, value) tuples. width: char width."""
        self.data = sorted(data)
        self.width = width
        self.label = label

    def render(self):
        """Return ASCII chart as string."""
        if not self.data:
            return f"{self.label}: (no data)"

        vals = [v for _, v in self.data]
        min_v, max_v = min(vals), max(vals)

        if min_v == max_v:
            sparkline = SPARKLINE[-1] * self.width
        else:
            norm = [(v - min_v) / (max_v - min_v) for v in vals]
            idx = [int(n * (len(SPARKLINE) - 1)) for n in norm]
            sparkline = "".join(SPARKLINE[i] for i in idx[:self.width])

        start = self.data[0][0]
        end = self.data[-1][0]
        return (f"{self.label}: {sparkline}\n"
                f"  {start} -> {end} (min={min_v:.1f}, max={max_v:.1f})")

def rolling_avg(data, window=3):
    """Compute rolling average over window of days."""
    result = []
    for i, (d, v) in enumerate(sorted(data)):
        vals = [vv for dd, vv in sorted(data) 
                if dd >= d - timedelta(days=window)]
        result.append((d, mean(vals)))
    return result

if __name__ == "__main__":
    today = date(2026, 9, 21)
    sample = [(today - timedelta(days=i), 50 + i*5) for i in range(10, -1, -1)]
    chart = TrendChart(sample, label="Trend")
    print(chart.render())
