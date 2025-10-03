"""
Performance Metrics Tracking
Simple metrics collection for monitoring system performance
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
from dataclasses import dataclass, field
import time
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricData:
    """Container for metric measurements"""
    count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    recent_values: deque = field(default_factory=lambda: deque(maxlen=100))

    @property
    def avg_duration(self) -> float:
        """Calculate average duration"""
        return self.total_duration / self.count if self.count > 0 else 0.0

    @property
    def p95_duration(self) -> float:
        """Calculate 95th percentile duration"""
        if not self.recent_values:
            return 0.0
        sorted_values = sorted(self.recent_values)
        index = int(len(sorted_values) * 0.95)
        return sorted_values[min(index, len(sorted_values) - 1)]


class PerformanceMetrics:
    """
    Simple performance metrics collector
    Tracks API endpoint response times and counts
    """

    def __init__(self):
        """Initialize metrics collector"""
        self._endpoint_metrics: Dict[str, MetricData] = defaultdict(MetricData)
        self._ai_metrics: Dict[str, MetricData] = defaultdict(MetricData)
        self._start_time = datetime.now(timezone.utc)

    def record_api_call(self, endpoint: str, duration_ms: float) -> None:
        """
        Record API endpoint call

        Args:
            endpoint: API endpoint path
            duration_ms: Request duration in milliseconds
        """
        metric = self._endpoint_metrics[endpoint]
        metric.count += 1
        metric.total_duration += duration_ms
        metric.min_duration = min(metric.min_duration, duration_ms)
        metric.max_duration = max(metric.max_duration, duration_ms)
        metric.recent_values.append(duration_ms)

    def record_ai_call(self, provider: str, duration_ms: float) -> None:
        """
        Record AI service call

        Args:
            provider: AI provider name (openai, anthropic, etc.)
            duration_ms: Call duration in milliseconds
        """
        metric = self._ai_metrics[provider]
        metric.count += 1
        metric.total_duration += duration_ms
        metric.min_duration = min(metric.min_duration, duration_ms)
        metric.max_duration = max(metric.max_duration, duration_ms)
        metric.recent_values.append(duration_ms)

    def get_api_stats(self) -> Dict[str, Dict]:
        """
        Get API endpoint statistics

        Returns:
            Dictionary with endpoint stats
        """
        stats = {}
        for endpoint, metric in self._endpoint_metrics.items():
            if metric.count > 0:
                stats[endpoint] = {
                    "calls": metric.count,
                    "avg_ms": round(metric.avg_duration, 2),
                    "min_ms": round(metric.min_duration, 2),
                    "max_ms": round(metric.max_duration, 2),
                    "p95_ms": round(metric.p95_duration, 2),
                }
        return stats

    def get_ai_stats(self) -> Dict[str, Dict]:
        """
        Get AI service statistics

        Returns:
            Dictionary with AI provider stats
        """
        stats = {}
        for provider, metric in self._ai_metrics.items():
            if metric.count > 0:
                stats[provider] = {
                    "calls": metric.count,
                    "avg_ms": round(metric.avg_duration, 2),
                    "min_ms": round(metric.min_duration, 2),
                    "max_ms": round(metric.max_duration, 2),
                    "p95_ms": round(metric.p95_duration, 2),
                }
        return stats

    def get_summary(self) -> Dict:
        """
        Get overall performance summary

        Returns:
            Summary statistics dictionary
        """
        total_api_calls = sum(m.count for m in self._endpoint_metrics.values())
        total_ai_calls = sum(m.count for m in self._ai_metrics.values())

        uptime = datetime.now(timezone.utc) - self._start_time
        uptime_seconds = uptime.total_seconds()

        return {
            "uptime_seconds": int(uptime_seconds),
            "uptime_formatted": str(uptime).split('.')[0],  # Remove microseconds
            "total_api_calls": total_api_calls,
            "total_ai_calls": total_ai_calls,
            "api_calls_per_minute": round(total_api_calls / (uptime_seconds / 60), 2) if uptime_seconds > 0 else 0,
            "endpoints_tracked": len(self._endpoint_metrics),
            "ai_providers_used": len(self._ai_metrics),
        }

    def get_slow_endpoints(self, threshold_ms: float = 1000) -> List[Dict]:
        """
        Get endpoints slower than threshold

        Args:
            threshold_ms: Threshold in milliseconds

        Returns:
            List of slow endpoints with stats
        """
        slow = []
        for endpoint, metric in self._endpoint_metrics.items():
            if metric.avg_duration > threshold_ms:
                slow.append({
                    "endpoint": endpoint,
                    "avg_ms": round(metric.avg_duration, 2),
                    "calls": metric.count,
                    "max_ms": round(metric.max_duration, 2),
                })
        return sorted(slow, key=lambda x: x["avg_ms"], reverse=True)

    def reset(self) -> None:
        """Reset all metrics"""
        self._endpoint_metrics.clear()
        self._ai_metrics.clear()
        self._start_time = datetime.now(timezone.utc)
        logger.info("Performance metrics reset")


# Global metrics instance
_global_metrics = PerformanceMetrics()


def get_metrics() -> PerformanceMetrics:
    """Get global metrics instance"""
    return _global_metrics


class TimingContext:
    """
    Context manager for timing operations

    Usage:
        with TimingContext("operation_name") as timer:
            # ... do work ...
            pass
        print(f"Took {timer.duration_ms}ms")
    """

    def __init__(self, name: str):
        """
        Initialize timing context

        Args:
            name: Operation name for logging
        """
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration_ms = 0.0

    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        if self.duration_ms > 1000:  # Log if > 1 second
            logger.warning(
                f"Slow operation: {self.name} took {self.duration_ms:.2f}ms",
                extra={"operation": self.name, "duration_ms": self.duration_ms}
            )
        elif self.duration_ms > 100:  # Log if > 100ms
            logger.info(
                f"Operation: {self.name} took {self.duration_ms:.2f}ms",
                extra={"operation": self.name, "duration_ms": self.duration_ms}
            )


# Export main components
__all__ = [
    "PerformanceMetrics",
    "get_metrics",
    "TimingContext",
]
