"""
CSRF Protection Middleware for FastAPI
Implements token-based CSRF protection for state-changing requests
"""

import secrets
from typing import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware

    Generates and validates CSRF tokens for POST, PUT, DELETE, PATCH requests.
    Uses double-submit cookie pattern for stateless validation.
    """

    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_secure: bool = False,
        cookie_httponly: bool = True,
        cookie_samesite: str = "lax",
        exempt_urls: list[str] = None
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.exempt_urls = exempt_urls or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]

    def generate_csrf_token(self) -> str:
        """Generate a secure random CSRF token"""
        return secrets.token_urlsafe(32)

    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        return any(path.startswith(exempt) for exempt in self.exempt_urls)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF for safe methods (GET, HEAD, OPTIONS, TRACE)
        if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            response = await call_next(request)

            # Set CSRF token cookie if not present
            if self.cookie_name not in request.cookies:
                csrf_token = self.generate_csrf_token()
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=self.cookie_httponly,
                    secure=self.cookie_secure,
                    samesite=self.cookie_samesite
                )

            return response

        # Check if URL is exempt
        if self.is_exempt(request.url.path):
            return await call_next(request)

        # Validate CSRF token for state-changing methods
        token_from_header = request.headers.get(self.header_name)
        token_from_cookie = request.cookies.get(self.cookie_name)

        if not token_from_header or not token_from_cookie:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing. Include X-CSRF-Token header."
            )

        if not secrets.compare_digest(token_from_header, token_from_cookie):
            raise HTTPException(
                status_code=403,
                detail="CSRF token validation failed"
            )

        # Token valid, proceed with request
        response = await call_next(request)
        return response


def add_csrf_protection(app, **kwargs):
    """
    Helper function to add CSRF protection to FastAPI app

    Usage:
        from middleware.csrf_middleware import add_csrf_protection
        add_csrf_protection(app, cookie_secure=True)
    """
    app.add_middleware(CSRFMiddleware, **kwargs)
