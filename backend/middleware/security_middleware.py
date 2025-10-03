"""
Security Middleware for NSEXP
Adds security headers and implements security best practices
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses
    Implements OWASP security best practices
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (relaxed for single-user app)
        if not request.url.path.startswith("/docs"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' http: https: ws: wss:;"
            )
        
        # Strict Transport Security (for production with HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        # Remove server header for security obscurity
        response.headers.pop("Server", None)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Limits requests per IP address per time window
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: defaultdict = defaultdict(list)
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request timestamps"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 60  # Keep only last minute
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    timestamp for timestamp in self.requests[ip]
                    if timestamp > cutoff_time
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = current_time
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        cutoff_time = current_time - 60  # Last minute
        
        # Get requests in last minute
        recent_requests = [
            timestamp for timestamp in self.requests[client_ip]
            if timestamp > cutoff_time
        ]
        
        return len(recent_requests) >= self.requests_per_minute
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request"""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics", "/favicon.ico"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"client_ip": client_ip, "path": request.url.path}
            )
            return Response(
                content='{"error": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        
        # Record request
        self.requests[client_ip].append(time.time())
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    CORS middleware with security considerations
    Restricts cross-origin requests appropriately
    """
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle CORS with security"""
        origin = request.headers.get("origin")
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
            response.headers["Access-Control-Max-Age"] = "3600"
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Basic input sanitization middleware
    Logs suspicious patterns in requests
    """
    
    SUSPICIOUS_PATTERNS = [
        "<script", "javascript:", "onerror=", "onclick=",
        "../", "..\\", "DROP TABLE", "UNION SELECT"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check for suspicious input patterns"""
        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in query_string:
                logger.warning(
                    f"Suspicious pattern detected in query: {pattern}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "path": request.url.path,
                        "pattern": pattern
                    }
                )
        
        # Check path
        path = str(request.url.path).lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern.lower() in path:
                logger.warning(
                    f"Suspicious pattern detected in path: {pattern}",
                    extra={
                        "client_ip": request.client.host if request.client else "unknown",
                        "path": request.url.path,
                        "pattern": pattern
                    }
                )
        
        return await call_next(request)
