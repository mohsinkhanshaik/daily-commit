"""Performance monitoring and metrics tracking for AI Pulse models.

Tracks inference latency, throughput, error rates, and token counts across
digest processing pipelines. Provides per-module statistics and anomaly alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class MetricType(Enum):
    LATENCY_MS = "latency_ms"
    THROUGHPUT_ITEMS_PER_SEC = "throughput"
    ERROR_RATE_PCT = "error_rate"
    TOKEN_COUNT = "tokens"


@dataclass
class Metric:
    """A single performance observation."""
    timestamp: datetime
    module: str
    metric_type: MetricType
    value: float

    def is_anomaly(self, baseline_mean: float, threshold_sigma: float = 2.0) -> bool:
        """Check if metric exceeds baseline + N sigma."""
        return abs(self.value - baseline_mean) > (threshold_sigma * 10.0)


@dataclass
class MetricsSeries:
    """Time series of metrics for analysis."""
    module: str
    metric_type: MetricType
    observations: list = field(default_factory=list)

    def add(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """Record a metric value."""
        ts = timestamp or datetime.utcnow()
        self.observations.append((ts, value))

    def mean(self) -> float:
        """Average over all observations."""
        if not self.observations:
            return 0.0
        return sum(v for _, v in self.observations) / len(self.observations)

    def p95(self) -> float:
        """95th percentile."""
        if not self.observations:
            return 0.0
        sorted_vals = sorted(v for _, v in self.observations)
        idx = int(len(sorted_vals) * 0.95)
        return sorted_vals[idx] if idx < len(sorted_vals) else sorted_vals[-1]

    def recent(self, minutes: int = 5) -> list:
        """Observations in the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [(ts, v) for ts, v in self.observations if ts >= cutoff]


@dataclass
class SystemMonitor:
    """Collect and report on system performance."""
    name: str
    series_map: dict = field(default_factory=dict)

    def track(self, module: str, metric_type: MetricType, value: float) -> None:
        """Record a performance metric."""
        key = (module, metric_type)
        if key not in self.series_map:
            series = MetricsSeries(module, metric_type)
            self.series_map[key] = series
        self.series_map[key].add(value)

    def report(self, module: Optional[str] = None) -> str:
        """Generate a performance report."""
        lines = [f"Performance Report: {self.name}\n"]
        for (mod, metric_type), series in self.series_map.items():
            if module and mod != module:
                continue
            mean = series.mean()
            p95 = series.p95()
            recent_count = len(series.recent(minutes=5))
            lines.append(
                f"  {mod} / {metric_type.value}: "
                f"mean={mean:.2f} p95={p95:.2f} recent_5m={recent_count}"
            )
        return "\n".join(lines)

    def anomalies(self, threshold_sigma: float = 2.0) -> list:
        """Detect and return anomalous metrics."""
        alerts = []
        for (mod, metric_type), series in self.series_map.items():
            baseline = series.mean()
            for ts, val in series.recent(minutes=5):
                if abs(val - baseline) > (threshold_sigma * 10.0):
                    alerts.append(
                        f"ANOMALY: {mod}/{metric_type.value} = {val:.2f} "
                        f"(baseline {baseline:.2f})"
                    )
        return alerts


if __name__ == "__main__":
    monitor = SystemMonitor("digest-processor")

    monitor.track("digest_parser", MetricType.LATENCY_MS, 125.4)
    monitor.track("digest_parser", MetricType.LATENCY_MS, 118.2)
    monitor.track("digest_parser", MetricType.LATENCY_MS, 500.0)
    monitor.track("tagger", MetricType.THROUGHPUT_ITEMS_PER_SEC, 42.5)
    monitor.track("tagger", MetricType.ERROR_RATE_PCT, 0.2)
    monitor.track("entities", MetricType.TOKEN_COUNT, 8500)

    print(monitor.report())
    print("\nAnomalies detected:")
    for alert in monitor.anomalies():
        print(f"  {alert}")
