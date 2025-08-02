import logging
import time
from typing import Dict, List, Optional

try:
    from fastapi import Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    # FastAPI not available in test environment
    FASTAPI_AVAILABLE = False
    Request = None
    Response = None
    BaseHTTPMiddleware = None

logger = logging.getLogger(__name__)


if FASTAPI_AVAILABLE:

    class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
        """Middleware to monitor API performance and response times"""

        def __init__(self, app, enable_detailed_logging: bool = True):
            super().__init__(app)
            self.enable_detailed_logging = enable_detailed_logging
            self.metrics: Dict[str, List[float]] = {}

        async def dispatch(self, request: Request, call_next):
            """Monitor request processing time"""
            start_time = time.time()

            # Process the request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Track metrics
            endpoint = f"{request.method} {request.url.path}"
            self._record_metric(endpoint, process_time)

            # Add performance header
            response.headers["X-Process-Time"] = str(process_time)

            # Log performance if enabled
            if self.enable_detailed_logging:
                self._log_performance(request, response, process_time)

            return response

        def _record_metric(self, endpoint: str, process_time: float):
            """Record performance metric for endpoint"""
            if endpoint not in self.metrics:
                self.metrics[endpoint] = []

            # Keep only last 100 measurements to prevent memory bloat
            if len(self.metrics[endpoint]) >= 100:
                self.metrics[endpoint].pop(0)

            self.metrics[endpoint].append(process_time)

        def _log_performance(
            self, request: Request, response: Response, process_time: float
        ):
            """Log performance information"""
            endpoint = f"{request.method} {request.url.path}"
            status_code = response.status_code

            # Determine log level based on performance and status
            if process_time > 5.0:  # Very slow requests
                log_level = logging.WARNING
                performance_indicator = "SLOW"
            elif process_time > 2.0:  # Moderately slow requests
                log_level = logging.INFO
                performance_indicator = "MODERATE"
            else:
                log_level = logging.DEBUG
                performance_indicator = "FAST"

            # Log with appropriate level
            logger.log(
                log_level,
                f"[{performance_indicator}] {endpoint} - {status_code} - {process_time:.3f}s",
            )

            # Log additional warning for very slow requests
            if process_time > 5.0:
                avg_time = self.get_average_response_time(endpoint)
                logger.warning(
                    f"Performance bottleneck detected: {endpoint} took {process_time:.3f}s "
                    f"(avg: {avg_time:.3f}s)"
                )

        def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
            """Get performance metrics summary for all endpoints"""
            summary = {}

            for endpoint, times in self.metrics.items():
                if times:
                    summary[endpoint] = {
                        "avg_time": sum(times) / len(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "request_count": len(times),
                        "total_time": sum(times),
                    }

            return summary

        def get_average_response_time(self, endpoint: str) -> float:
            """Get average response time for specific endpoint"""
            if endpoint in self.metrics and self.metrics[endpoint]:
                return sum(self.metrics[endpoint]) / len(self.metrics[endpoint])
            return 0.0

        def get_slowest_endpoints(self, limit: int = 5) -> List[Dict[str, float]]:
            """Get the slowest endpoints by average response time"""
            summary = self.get_metrics_summary()

            sorted_endpoints = sorted(
                summary.items(), key=lambda x: x[1]["avg_time"], reverse=True
            )

            return [
                {
                    "endpoint": endpoint,
                    "avg_time": metrics["avg_time"],
                    "request_count": metrics["request_count"],
                }
                for endpoint, metrics in sorted_endpoints[:limit]
            ]

        def clear_metrics(self):
            """Clear all collected metrics"""
            self.metrics.clear()
            logger.info("Performance metrics cleared")

else:
    # Stub class when FastAPI is not available
    class PerformanceMonitoringMiddleware:
        def __init__(self, app, enable_detailed_logging: bool = True):
            self.app = app

        async def __call__(self, scope, receive, send):
            # Pass through to the app without monitoring in test mode
            await self.app(scope, receive, send)


class QueryPerformanceTracker:
    """Track performance of specific operations like database queries and AI calls"""

    def __init__(self):
        self.operation_metrics: Dict[str, List[float]] = {}

    def track_operation(self, operation_name: str, duration: float):
        """Track duration of a specific operation"""
        if operation_name not in self.operation_metrics:
            self.operation_metrics[operation_name] = []

        # Keep only last 50 measurements per operation
        if len(self.operation_metrics[operation_name]) >= 50:
            self.operation_metrics[operation_name].pop(0)

        self.operation_metrics[operation_name].append(duration)

        # Log slow operations
        if duration > 3.0:
            avg_duration = sum(self.operation_metrics[operation_name]) / len(
                self.operation_metrics[operation_name]
            )
            logger.warning(
                f"Slow operation detected: {operation_name} took {duration:.3f}s "
                f"(avg: {avg_duration:.3f}s)"
            )

    def get_operation_stats(self, operation_name: str) -> Optional[Dict[str, float]]:
        """Get statistics for a specific operation"""
        if (
            operation_name not in self.operation_metrics
            or not self.operation_metrics[operation_name]
        ):
            return None

        times = self.operation_metrics[operation_name]
        return {
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "call_count": len(times),
            "total_time": sum(times),
        }

    def get_all_operations_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all tracked operations"""
        summary = {}
        for operation_name in self.operation_metrics:
            stats = self.get_operation_stats(operation_name)
            if stats:
                summary[operation_name] = stats
        return summary


# Global tracker instance for operation monitoring
query_performance_tracker = QueryPerformanceTracker()


def track_performance(operation_name: str):
    """Decorator to track performance of functions"""

    def decorator(func):
        import asyncio
        import inspect

        if inspect.iscoroutinefunction(func):
            # Async function wrapper
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    query_performance_tracker.track_operation(operation_name, duration)

            return async_wrapper
        else:
            # Sync function wrapper
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    query_performance_tracker.track_operation(operation_name, duration)

            return sync_wrapper

    return decorator
