"""
Content Security Policy (CSP) Middleware for FastAPI
Adds CSP headers to prevent XSS, clickjacking, and other code injection attacks
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CSPMiddleware(BaseHTTPMiddleware):
    """
    Content Security Policy Middleware

    Adds security headers to all responses to prevent various attacks.
    """

    def __init__(
        self,
        app,
        policy: str = None,
        report_only: bool = False
    ):
        super().__init__(app)
        self.report_only = report_only

        # Default CSP policy
        self.policy = policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:* wss://localhost:*; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add CSP header
        header_name = (
            "Content-Security-Policy-Report-Only" if self.report_only
            else "Content-Security-Policy"
        )
        response.headers[header_name] = self.policy

        # Add additional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


def add_csp_protection(app, policy: str = None, report_only: bool = False):
    """
    Helper function to add CSP protection to FastAPI app

    Usage:
        from middleware.csp_middleware import add_csp_protection
        add_csp_protection(app, report_only=False)
    """
    app.add_middleware(CSPMiddleware, policy=policy, report_only=report_only)
