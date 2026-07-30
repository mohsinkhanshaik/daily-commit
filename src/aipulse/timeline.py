"""timeline.py - Per-entity event timelines.

Transforms news items into searchable event sequences per entity.
Each EntityTimeline collects events (date, headline, summary) for one
entity and supports filtering by date range and category.
"""

from datetime import date
from dataclasses import dataclass, field


@dataclass
class Event:
    """A single news event for an entity."""
    event_date: date
    headline: str
    summary: str
    category: str = "other"


@dataclass
class EntityTimeline:
    """Timeline of events for one company or model."""
    entity_name: str
    events: list[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        """Append an event to the timeline."""
        self.events.append(event)

    def filter_by_date(self, start: date, end: date) -> list[Event]:
        """Return events in [start, end] range."""
        return [e for e in self.events if start <= e.event_date <= end]

    def filter_by_category(self, cat: str) -> list[Event]:
        """Return events matching category."""
        return [e for e in self.events if e.category == cat]

    def sorted_events(self) -> list[Event]:
        """Return events sorted by date, newest first."""
        return sorted(self.events, key=lambda e: e.event_date, reverse=True)
\n\ndef timeline_for(entity_name: str, events: list[Event]) -> EntityTimeline:\n    \"\"\"Build a timeline for an entity from raw events.\"\"\"\n    timeline = EntityTimeline(entity_name)\n    for event in events:\n        timeline.add_event(event)\n    return timeline\n\n\nif __name__ == \"__main__\":\n    from datetime import timedelta\n\n    today = date(2026, 7, 30)\n    openai_events = [\n        Event(today - timedelta(days=3), \"GPT-5.6 released\",\n              \"OpenAI launches three variants\", \"products\"),\n        Event(today - timedelta(days=1), \"Ultra mode\",\n              \"Max reasoning with sub-agents\", \"research\"),\n    ]\n    timeline = timeline_for(\"OpenAI\", openai_events)\n    print(f\"Timeline for {timeline.entity_name}:\")\n    for event in timeline.sorted_events():\n        print(f\"  {event.event_date}: {event.headline}\")
