"""Per-entity event timelines across digests.

Build chronological event sequences for each company and model, enabling
tracking of entity evolution over time. Timelines support range queries and
event aggregation for trend analysis.
"""

from dataclasses import dataclass, field
from datetime import date
from collections import defaultdict

@dataclass
class TimelineEvent:
  """Single event in an entity's history."""
  event_date: date
  headline: str
  summary: str
  url: str = ""

@dataclass
class EntityTimeline:
  """Chronological event sequence for one entity."""
  entity_name: str
  events: list = field(default_factory=list)

  def add_event(self, event: TimelineEvent) -> None:
    """Add event to timeline, maintaining chronological order."""
    self.events.append(event)
    self.events.sort(key=lambda e: e.event_date)

  def events_in_range(self, start: date, end: date) -> list:
    """Get events within a date range (inclusive)."""
    return [e for e in self.events if start <= e.event_date <= end]

class TimelineBuilder:
  """Build timelines from digest items grouped by entity."""
  def __init__(self):
    self.timelines: dict = {}

  def add_item(self, entity: str, event_date: date, headline: str, summary: str, url: str = "") -> None:
    """Add item from a digest to entity timeline."""
    if entity not in self.timelines:
      self.timelines[entity] = EntityTimeline(entity)
    evt = TimelineEvent(event_date, headline, summary, url)
    self.timelines[entity].add_event(evt)

  def get_timeline(self, entity: str) -> EntityTimeline:
    """Retrieve timeline for an entity or empty if unknown."""
    return self.timelines.get(entity, EntityTimeline(entity))

if __name__ == "__main__":
  from datetime import date
  builder = TimelineBuilder()
  builder.add_item("OpenAI", date(2026, 7, 28), "GPT-5.5 launch", "OpenAI releases GPT-5.5")
  builder.add_item("OpenAI", date(2026, 7, 29), "Pacing initiative", "Staff petition on frontier AI pacing")
  builder.add_item("Anthropic", date(2026, 7, 1), "Claude Fable 5", "Most capable model released")
  openai_tl = builder.get_timeline("OpenAI")
  print(f"OpenAI events: {len(openai_tl.events)}")
  for evt in openai_tl.events:
    print(f"  {evt.event_date}: {evt.headline}")
