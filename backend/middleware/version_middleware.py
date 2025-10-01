"""
API Version Validation Middleware
Validates API version and provides helpful errors for invalid versions
"""
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import get_logger

logger = get_logger(__name__)


class VersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate API version in request path
    """

    # Supported API versions
    SUPPORTED_VERSIONS = {"v1"}
    DEFAULT_VERSION = "v1"

    # Paths that don't require version checking
    EXCLUDED_PATHS = {"/health", "/metrics", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Validate API version in request path

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response object
        """
        path = request.url.path

        # Skip version checking for excluded paths
        if path in self.EXCLUDED_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        # Extract version from path (e.g., /api/v1/chapters → v1)
        path_parts = path.split("/")

        if len(path_parts) < 3:
            # Path doesn't include version, this is fine (will use default)
            return await call_next(request)

        # Check if second part after /api/ looks like a version
        potential_version = path_parts[2]

        if not potential_version.startswith("v"):
            # Not a version specifier, continue
            return await call_next(request)

        # Validate version
        if potential_version not in self.SUPPORTED_VERSIONS:
            logger.warning(
                f"Invalid API version requested: {potential_version}",
                extra={
                    "path": path,
                    "requested_version": potential_version,
                    "supported_versions": list(self.SUPPORTED_VERSIONS),
                }
            )

            return JSONResponse(
                status_code=404,
                content={
                    "error": "API version not found",
                    "message": f"Version '{potential_version}' is not available. Current version: {self.DEFAULT_VERSION}",
                    "requested_version": potential_version,
                    "available_versions": list(self.SUPPORTED_VERSIONS),
                    "default_version": self.DEFAULT_VERSION,
                    "documentation": "/docs",
                }
            )

        # Version is valid, store in request state for logging
        request.state.api_version = potential_version

        # Continue processing
        return await call_next(request)
