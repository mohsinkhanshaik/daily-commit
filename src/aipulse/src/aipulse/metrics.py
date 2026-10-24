"""Lightweight performance monitoring and metrics collection for AI Pulse.

Provides instrumentation decorators for timing operations, tracking cache
hit rates, counting processed items, measuring memory footprint, and
aggregating performance statistics across time windows.
"""
import time
import functools
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Any, Optional
import sys


@dataclass
class TimingStats:
    """Aggregates timing statistics for a single operation."""
    calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0

    def add(self, elapsed: float) -> None:
        self.calls += 1
        self.total_time += elapsed
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)

    @property
    def average(self) -> float:
        return self.total_time / self.calls if self.calls > 0 else 0.0


class MetricsCollector:
    """Collects and reports performance metrics with time-windowed aggregation."""

    def __init__(self, window_size: int = 100):
        self.timings: dict[str, TimingStats] = defaultdict(TimingStats)
        self.counters: dict[str, int] = defaultdict(int)
        self.cache_hits: dict[str, tuple[int, int]] = {}
        self.memory_samples: dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.start_times: dict[str, float] = {}

    def track_time(self, key: str, elapsed: float) -> None:
        """Record elapsed time for an operation."""
        self.timings[key].add(elapsed)

    def increment(self, key: str, amount: int = 1) -> None:
        """Increment a counter."""
        self.counters[key] += amount

    def record_cache_access(self, key: str, hit: bool) -> None:
        """Track cache hit or miss."""
        hits, total = self.cache_hits.get(key, (0, 0))
        self.cache_hits[key] = (hits + (1 if hit else 0), total + 1)

    def sample_memory(self, key: str, mb: float) -> None:
        """Sample current memory usage in MB."""
        self.memory_samples[key].append(mb)

    def report(self) -> str:
        """Generate a formatted performance report."""
        lines = ['Performance Metrics Report']
        lines.append('='*40)

        if self.timings:
            lines.append('Timing Statistics (seconds):')
            for key, stats in sorted(self.timings.items()):
                avg = stats.average
                lines.append(f'  {key}: {stats.calls} calls, avg {avg:.4f}s, '
                           f'min {stats.min_time:.4f}s, max {stats.max_time:.4f}s')

        if self.counters:
            lines.append('Counters:')
            for key, count in sorted(self.counters.items()):
                lines.append(f'  {key}: {count}')

        if self.cache_hits:
            lines.append('Cache Statistics:')
            for key, (hits, total) in sorted(self.cache_hits.items()):
                rate = 100 * hits / total if total > 0 else 0
                lines.append(f'  {key}: {rate:.1f}% hit rate ({hits}/{total})')

        return '\n'.join(lines)

_global_metrics = MetricsCollector()


def time_operation(key: str) -> Callable:
    """Decorator to time a function and record in global metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start
                _global_metrics.track_time(key, elapsed)
        return wrapper
    return decorator


if __name__ == '__main__':
    @time_operation('sample_analysis')
    def analyze_digests(count: int) -> None:
        """Simulate digest analysis pipeline."""
        time.sleep(0.01 * count)
        for i in range(count):
            if i % 10 == 0:
                _global_metrics.increment('digests_processed')
            _global_metrics.record_cache_access('query_cache', i % 3 == 0)

    analyze_digests(30)
    print(_global_metrics.report())
