"""Real-time event notification engine with configurable alert rules.

Evaluates incoming digest items against rule definitions, generates alerts
for entity mentions, category thresholds, and trending topics, and dispatches
through email, webhook, and in-app adapters. Stub implementations support
extension with real backends.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
from datetime import datetime
from enum import Enum


class AlertType(Enum):
    ENTITY_MENTION = "entity_mention"
    SCORE_THRESHOLD = "score_threshold"
    TREND_SPIKE = "trend_spike"
    CATEGORY_SHIFT = "category_shift"

@dataclass
class NotificationRule:
    rule_id: str
    alert_type: AlertType
    target: str
    threshold: float = 0.5
    enabled: bool = True

@dataclass
class Alert:
    alert_id: str
    rule_id: str
    alert_type: AlertType
    headline: str
    context: str
    source_url: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "info"

class NotificationEngine:
    """Evaluates rules and generates alerts from news items."""

    def __init__(self):
        self.rules = {}
        self.alert_history = []

    def register_rule(self, rule: NotificationRule) -> None:
        """Register an alert rule."""
        self.rules[rule.rule_id] = rule

    def evaluate(self, headline: str, entities: list, category: str,
                 score: float, source_url: str = "") -> list:
        """Evaluate rules against a news item; return matching alerts."""
        alerts = []
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            matched = False
            if rule.alert_type == AlertType.ENTITY_MENTION:
                matched = rule.target in entities
            elif rule.alert_type == AlertType.SCORE_THRESHOLD:
                matched = score >= rule.threshold
            elif rule.alert_type == AlertType.CATEGORY_SHIFT:
                matched = category != rule.target

            if matched:
                alert = Alert(
                    alert_id=f"alert_{len(self.alert_history)}",
                    rule_id=rule_id,
                    alert_type=rule.alert_type,
                    headline=headline,
                    context=f"Matched rule: {rule.target}",
                    source_url=source_url,
                    severity="warning" if score > 0.7 else "info"
                )
                alerts.append(alert)
                self.alert_history.append(alert)
        return alerts

    def dispatch_email(self, alert: Alert, recipient: str) -> bool:
        """Stub: dispatch alert via email."""
        print(f"[EMAIL] To {recipient}: {alert.headline}")
        return True

    def dispatch_webhook(self, alert: Alert, webhook_url: str) -> bool:
        """Stub: dispatch alert to webhook."""
        print(f"[WEBHOOK] POST {webhook_url}: {alert.alert_type.value}")
        return True

    def dispatch_inapp(self, alert: Alert, user_id: str) -> bool:
        """Stub: create in-app notification."""
        print(f"[INAPP] User {user_id}: {alert.headline}")
        return True


if __name__ == "__main__":
    engine = NotificationEngine()

    engine.register_rule(NotificationRule(
        rule_id="rule_1",
        alert_type=AlertType.ENTITY_MENTION,
        target="Claude",
        enabled=True
    ))
    engine.register_rule(NotificationRule(
        rule_id="rule_2",
        alert_type=AlertType.SCORE_THRESHOLD,
        target="high_impact",
        threshold=0.75,
        enabled=True
    ))

    news_items = [
        ("Claude beats benchmark on 3D tasks", ["Claude", "Anthropic"], "research", 0.8),
        ("New chip shortage confirmed", ["TSMC", "Nvidia"], "chips", 0.6),
        ("OpenAI safety talks continue", ["OpenAI"], "policy", 0.7),
    ]

    print("=== AI Pulse Notification Engine Demo ===")
    print()
    for headline, entities, category, score in news_items:
        alerts = engine.evaluate(headline, entities, category, score)
        for alert in alerts:
            print(f"Alert: {alert.headline} (severity: {alert.severity})")
            engine.dispatch_email(alert, "subscriber@example.com")
            engine.dispatch_webhook(alert, "https://api.example.com/alerts")
            engine.dispatch_inapp(alert, "user_123")
        if not alerts:
            print(f"No alerts: {headline}")
        print()

    print(f"Total alerts generated: {len(engine.alert_history)}")
