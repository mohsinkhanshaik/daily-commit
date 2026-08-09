"""Weekly report generator for AI Pulse.

Aggregates digests and trends across a week, producing curated
markdown reports with top stories, rising topics, and takeaways."""

from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class WeeklyReport:
    week_start: datetime
    week_end: datetime
    items: list = None
    by_category: dict = None

    def __post_init__(self):
        if self.items is None:
            self.items = []
        if self.by_category is None:
            self.by_category = defaultdict(list)

    def render_markdown(self, top_n=5):
        """Generate weekly markdown report."""
        lines = [f"# Weekly Report {self.week_start.date()} to {self.week_end.date()}\n"]
        lines.append(f"Digest items processed: {len(self.items)}\n")
        lines.append("## Top Stories by Category\n")
        for cat in sorted(self.by_category.keys()):
            items = self.by_category[cat][:top_n]
            lines.append(f"### {cat}\n")
            for item in items:
                lines.append(f"- {item}")
        return ''.join(lines)


def week_range(end_date):
    """Compute week start/end for a given end date."""
    end = end_date if isinstance(end_date, datetime) else datetime.fromisoformat(str(end_date))
    start = end - timedelta(days=6)
    return start, end


if __name__ == "__main__":
    from datetime import date
    end = datetime(2026, 8, 9)
    start, end = week_range(end)
    report = WeeklyReport(week_start=start, week_end=end)
    report.items = ["AI chip export deal approved", "OpenAI IPO filing expected", "Anthropic hires new officer"]
    report.by_category["policy"] = report.items[:2]
    report.by_category["other"] = report.items[2:]
    print(report.render_markdown())
