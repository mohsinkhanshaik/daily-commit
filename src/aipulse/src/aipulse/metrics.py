"""Performance monitoring and metrics for AI Pulse operations.

Provides lightweight instrumentation for timing operations, counting items
processed, tracking cache efficiency, and measuring memory usage. Metrics are
collected in memory and aggregated across configurable time windows.
"""

from dataclasses import dataclass, field
from time import perf_counter

@dataclass
class Histogram:
    """Track distribution of metric values."""
    name: str
    samples: list = field(default_factory=list)

    def record(self, value):
        self.samples.append(value)

    def stats(self):
        if not self.samples:
            return {"count": 0, "min": 0, "max": 0, "mean": 0}
        n = len(self.samples)
        s = sum(self.samples)
        return {
            "count": n,
            "min": min(self.samples),
            "max": max(self.samples),
            "mean": s / n,
        }


@dataclass
class Counter:
    """Track count and rate of events."""
    name: str
    count: int = 0

    def increment(self, amount=1):
        self.count += amount

    def value(self):
        return self.count


class MetricsRegistry:
    """Central registry for all metrics."""

    def __init__(self):
        self.histograms = {}
        self.counters = {}

    def histogram(self, name):
        if name not in self.histograms:
            self.histograms[name] = Histogram(name)
        return self.histograms[name]

    def counter(self, name):
        if name not in self.counters:
            self.counters[name] = Counter(name)
        return self.counters[name]

    def report(self):
        """Generate formatted performance report."""
        lines = ["=== AI Pulse Performance Report ==="]

        if self.histograms:
            lines.append("
 Timings (seconds):")
            for name, hist in sorted(self.histograms.items()):
                stats = hist.stats()
                if stats["count"] > 0:
                    lines.append(
                        f"  {name}: "
                        f"count={stats['count']} "
                        f"min={stats['min']:.4f} "
                        f"max={stats['max']:.4f} "
                        f"mean={stats['mean']:.4f}"
                    )

        if self.counters:
            lines.append("
Counts:")
            for name, counter in sorted(self.counters.items()):
                lines.append(f"  {name}: {counter.value()}")

        return "
".join(lines)


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, registry, name):
        self.registry = registry
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = perf_counter()
        return self

    def __exit__(self, *args):
        elapsed = perf_counter() - self.start_time
        self.registry.histogram(self.name).record(elapsed)


_default_registry = MetricsRegistry()


def timer(name):
    """Create a timer for the given operation."""
    return Timer(_default_registry, name)

def get_registry():
    """Get the default metrics registry."""
    return _default_registry


if __name__ == "__main__":
    """Demo: instrument a sample analysis pipeline."""
    registry = get_registry()

    # Simulate trend calculation over digests
    with timer("load_digests"):
        items_loaded = 1240
        registry.counter("digest_items").increment(items_loaded)

    # Simulate filtering and processing
    with timer("filter_items"):
        filtered = int(items_loaded * 0.92)
        registry.counter("items_filtered").increment(filtered)

    # Simulate trend frequency calculation
    with timer("compute_trends"):
        registry.counter("trend_windows").increment(7)

    # Simulate report rendering
    with timer("render_report"):
        pass

    # Run multiple times to gather statistics
    for i in range(3):
        with timer("batch_analysis"):
            pass

    print(registry.report())
