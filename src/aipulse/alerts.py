"""Day 25: Threshold-based alerts for significant AI news events.

This module defines thresholds on news metrics (funding amounts, lab prominence,
policy impact) and checks news items against them to surface high-impact events.
Alerts enable users to monitor trends without reading every digest.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Callable, List


@dataclass
class Threshold:
    """A condition that triggers an alert."""
    name: str
    check_fn: Callable[[dict], bool] = field(default=None)
    description: str = ""


@dataclass
class Alert:
    """An alert triggered by a news item crossing a threshold."""
    threshold_name: str
    headline: str
    reason: str
    severity: str  # "high", "medium", "low"


def define_threshold(name: str, check_fn: Callable, desc: str = "") -> Threshold:
    """Create a threshold with a checking function."""
    return Threshold(name=name, check_fn=check_fn, description=desc)


def check_thresholds(item: dict, thresholds: List[Threshold]) -> List[Alert]:
    """Evaluate a news item against all thresholds; return triggered alerts."""
    alerts = []
    for t in thresholds:
        if t.check_fn(item):
            severity = "high" if "funding" in t.name.lower() else "medium"
            alerts.append(Alert(
                threshold_name=t.name,
                headline=item.get("headline", "Unknown"),
                reason=f"Matched {t.name}: {t.description}",
                severity=severity
            ))
    return alerts


def format_alert_report(alerts: List[Alert]) -> str:
    """Format alerts as a readable report."""
    if not alerts:
        return "No alerts triggered today."
    report = [f"Alert Report: {len(alerts)} event(s)\n"]
    for alert in alerts:
        report.append(f"[{alert.severity.upper()}] {alert.threshold_name}")
        report.append(f"  Headline: {alert.headline}")
        report.append(f"  Reason: {alert.reason}\n")
    return "\n".join(report)


if __name__ == "__main__":
    # Demo: define thresholds and check sample items
    funding_500m = define_threshold(
        "Funding > 500M",
        lambda x: "funding" in str(x).lower() and any(amt in str(x) for amt in ["500M", "1B", "800M"]),
        "Major funding round for AI company"
    )
    top_lab_model = define_threshold(
        "OpenAI/DeepSeek Release",
        lambda x: any(lab in str(x) for lab in ["OpenAI", "DeepSeek", "Anthropic", "Meta"]),
        "New model from frontier lab"
    )
    policy_eu = define_threshold(
        "EU AI Act",
        lambda x: "EU" in str(x) or "Europe" in str(x) or "regulation" in str(x).lower(),
        "AI regulation or policy change"
    )

    sample_items = [
        {"headline": "OpenAI raises $1B Series funding", "source": "TechCrunch"},
        {"headline": "TSMC expands chip capacity", "source": "Reuters"},
        {"headline": "EU AI Act enforcement begins", "source": "EU Press"},
    ]

    thresholds = [funding_500m, top_lab_model, policy_eu]
    all_alerts = []
    for item in sample_items:
        all_alerts.extend(check_thresholds(item, thresholds))

    print(format_alert_report(all_alerts))
