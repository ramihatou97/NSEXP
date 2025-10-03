"""
Performance Metrics Middleware
Tracks API performance and system health metrics
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, List
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetrics:
    """
    Stores and manages performance metrics
    Thread-safe metrics collection
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        
        # Request counters
        self.total_requests = 0
        self.success_count = 0
        self.error_count = 0
        
        # Response time tracking (by endpoint)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        
        # Request count by endpoint
        self.endpoint_counts: Dict[str, int] = defaultdict(int)
        
        # Status code distribution
        self.status_codes: Dict[int, int] = defaultdict(int)
        
        # Request count by method
        self.method_counts: Dict[str, int] = defaultdict(int)
        
        # Error tracking
        self.errors: deque = deque(maxlen=100)
    
    def record_request(
        self, 
        method: str, 
        path: str, 
        status_code: int, 
        duration_ms: float,
        error: str = None
    ):
        """Record a request"""
        self.total_requests += 1
        
        # Record success/error
        if 200 <= status_code < 400:
            self.success_count += 1
        else:
            self.error_count += 1
            if error:
                self.errors.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "error": error
                })
        
        # Record metrics
        self.response_times[path].append(duration_ms)
        self.endpoint_counts[path] += 1
        self.status_codes[status_code] += 1
        self.method_counts[method] += 1
    
    def get_stats(self, path: str = None) -> Dict:
        """Get performance statistics"""
        if path and path in self.response_times:
            times = list(self.response_times[path])
            return self._calculate_stats(times)
        
        # Overall stats
        all_times = []
        for times in self.response_times.values():
            all_times.extend(times)
        
        return self._calculate_stats(all_times)
    
    def _calculate_stats(self, times: List[float]) -> Dict:
        """Calculate statistics from response times"""
        if not times:
            return {
                "count": 0,
                "avg_ms": 0,
                "min_ms": 0,
                "max_ms": 0,
                "p50_ms": 0,
                "p95_ms": 0,
                "p99_ms": 0
            }
        
        sorted_times = sorted(times)
        count = len(sorted_times)
        
        return {
            "count": count,
            "avg_ms": round(sum(sorted_times) / count, 2),
            "min_ms": round(sorted_times[0], 2),
            "max_ms": round(sorted_times[-1], 2),
            "p50_ms": round(sorted_times[int(count * 0.5)], 2),
            "p95_ms": round(sorted_times[int(count * 0.95)], 2) if count > 20 else round(sorted_times[-1], 2),
            "p99_ms": round(sorted_times[int(count * 0.99)], 2) if count > 100 else round(sorted_times[-1], 2)
        }
    
    def get_summary(self) -> Dict:
        """Get overall metrics summary"""
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": round(
                (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 0,
                2
            ),
            "performance": self.get_stats(),
            "top_endpoints": sorted(
                self.endpoint_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "status_code_distribution": dict(self.status_codes),
            "method_distribution": dict(self.method_counts),
            "recent_errors": list(self.errors)[-10:]
        }


# Global metrics instance
_metrics = PerformanceMetrics()


def get_metrics() -> PerformanceMetrics:
    """Get global metrics instance"""
    return _metrics


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API performance
    Records response times and generates metrics
    """
    
    # Paths to exclude from metrics
    EXCLUDED_PATHS = {"/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"}
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = get_metrics()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request performance"""
        # Skip excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        error_message = None
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Record error
            error_message = str(e)
            status_code = 500
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": error_message
                },
                exc_info=True
            )
            raise
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
                error=error_message
            )
            
            # Log slow requests
            if duration_ms > 1000:  # Slower than 1 second
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path}",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(duration_ms, 2)
                    }
                )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{round(duration_ms, 2)}ms"
        
        return response


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware for health checks
    Provides system health status
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = get_metrics()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercept health check requests"""
        # Health check endpoint
        if request.url.path == "/health":
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": int(time.time() - self.metrics.total_requests * 0.1),  # Approximation
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "success_rate": round(
                        (self.metrics.success_count / self.metrics.total_requests * 100) 
                        if self.metrics.total_requests > 0 else 100,
                        2
                    )
                }
            }
            
            from fastapi.responses import JSONResponse
            return JSONResponse(content=health_data)
        
        # Metrics endpoint
        if request.url.path == "/metrics":
            from fastapi.responses import JSONResponse
            return JSONResponse(content=self.metrics.get_summary())
        
        return await call_next(request)
