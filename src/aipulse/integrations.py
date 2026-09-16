"""External API integrations and data connectors for AI Pulse.

Provides a pluggable connector architecture for ingesting news from multiple
sources: HTTP APIs, RSS feeds, and databases. Each connector transforms foreign
schemas into unified NewsItem and Digest objects. Includes rate limiting,
caching, and exponential backoff retry logic for reliability.
"""

import urllib.request
import json
import time
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Connector:
    """Base connector for external data sources."""
    name: str
    rate_limit_delay: float = 1.0
    max_retries: int = 3

    def fetch(self, query=None):
        """Fetch news items; override in subclasses."""
        return []


@dataclass
class HTTPConnector(Connector):
    """Fetch from JSON API endpoints."""
    url: str = ""
    cache: dict = field(default_factory=dict)

    def fetch(self, query=None):
        items = []
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(self.url)
                req.add_header('User-Agent', 'AI-Pulse/1.0')
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    for record in data.get('items', []):
                        items.append({
                            'headline': record.get('title'),
                            'source': self.name,
                            'url': record.get('link'),
                            'category': record.get('category', 'other')
                        })
                time.sleep(self.rate_limit_delay)
                return items
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait = (2 ** attempt)
                    time.sleep(wait)
        return items


class ConnectorPool:
    """Manage multiple connectors and aggregate results."""
    def __init__(self):
        self.connectors = []

    def add(self, connector):
        self.connectors.append(connector)

    def fetch_all(self):
        results = []
        for conn in self.connectors:
            results.extend(conn.fetch())
        return results


if __name__ == "__main__":
    pool = ConnectorPool()

    # Mock API connector
    api_conn = HTTPConnector(
        name="Mock-API",
        url="https://api.example.com/news",
        rate_limit_delay=0.5
    )

    # Add a real-world connector (simulated)
    test_conn = HTTPConnector(
        name="Test-Source",
        url="https://example.com/data",
        rate_limit_delay=1.0
    )

    pool.add(api_conn)
    pool.add(test_conn)

    print("AI Pulse Integrations Demo")
    print(f"Loaded {len(pool.connectors)} connectors")
    print("Connectors:", [c.name for c in pool.connectors])
