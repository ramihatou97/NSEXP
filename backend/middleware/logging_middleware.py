"""
Logging Middleware for Request/Response Tracking
Logs all API requests with timing, status codes, and errors
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import get_logger, log_with_context
from utils.metrics import get_metrics

logger = get_logger(__name__)
metrics = get_metrics()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    Tracks timing, status codes, and errors
    """

    # Endpoints to exclude from logging (reduce noise)
    EXCLUDED_PATHS = {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response object
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip logging for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Log incoming request
        log_with_context(
            logger,
            "info",
            f"Incoming request: {request.method} {request.url.path}",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_host=request.client.host if request.client else None,
        )

        # Process request
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            log_with_context(
                logger,
                "info",
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Record performance metrics
            metrics.record_api_call(request.url.path, duration_ms)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            log_with_context(
                logger,
                "error",
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
            )

            # Re-raise exception to be handled by FastAPI
            raise
