"""
Custom exceptions for NSEXP
Standardized error handling across the application
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class NSEXPException(Exception):
    """Base exception for NSEXP"""
    
    def __init__(
        self, 
        message: str, 
        code: str, 
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "details": self.details,
                "status_code": self.status_code
            }
        }


# Resource not found exceptions
class ResourceNotFoundError(NSEXPException):
    """Resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            code=f"{resource_type.upper()}_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
            status_code=status.HTTP_404_NOT_FOUND
        )


class ChapterNotFoundError(ResourceNotFoundError):
    """Chapter not found"""
    
    def __init__(self, chapter_id: str):
        super().__init__("Chapter", chapter_id)


class ReferenceNotFoundError(ResourceNotFoundError):
    """Reference not found"""
    
    def __init__(self, reference_id: str):
        super().__init__("Reference", reference_id)


class QASessionNotFoundError(ResourceNotFoundError):
    """Q&A session not found"""
    
    def __init__(self, session_id: str):
        super().__init__("QA Session", session_id)


# Validation exceptions
class ValidationError(NSEXPException):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, **(details or {})},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class InvalidSpecialtyError(ValidationError):
    """Invalid neurosurgical specialty"""
    
    def __init__(self, specialty: str, valid_specialties: list):
        super().__init__(
            message=f"Invalid specialty: {specialty}",
            field="specialty",
            details={
                "provided": specialty,
                "valid_options": valid_specialties
            }
        )


class InvalidContentError(ValidationError):
    """Invalid content"""
    
    def __init__(self, message: str):
        super().__init__(message=message, field="content")


# AI service exceptions
class AIServiceError(NSEXPException):
    """AI service error"""
    
    def __init__(self, message: str, provider: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AI_SERVICE_ERROR",
            details={"provider": provider, **(details or {})},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class AllProvidersFailedError(AIServiceError):
    """All AI providers failed"""
    
    def __init__(self, attempted_providers: list):
        super().__init__(
            message="All AI providers failed to respond",
            details={"attempted_providers": attempted_providers}
        )


class AIRateLimitError(AIServiceError):
    """AI provider rate limit exceeded"""
    
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            provider=provider,
            details={"retry_after_seconds": retry_after}
        )


class AITokenLimitError(AIServiceError):
    """AI token limit exceeded"""
    
    def __init__(self, provider: str, token_count: int, max_tokens: int):
        super().__init__(
            message=f"Token limit exceeded for {provider}",
            provider=provider,
            details={
                "token_count": token_count,
                "max_tokens": max_tokens
            }
        )


# Database exceptions
class DatabaseError(NSEXPException):
    """Database error"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection error"""
    
    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            message="Failed to connect to database",
            details=details
        )


# PDF processing exceptions
class PDFProcessingError(NSEXPException):
    """PDF processing error"""
    
    def __init__(self, message: str, filename: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="PDF_PROCESSING_ERROR",
            details={"filename": filename, **(details or {})},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class PDFEncryptedError(PDFProcessingError):
    """PDF is encrypted"""
    
    def __init__(self, filename: str):
        super().__init__(
            message="PDF file is encrypted",
            filename=filename
        )


class PDFCorruptedError(PDFProcessingError):
    """PDF is corrupted"""
    
    def __init__(self, filename: str):
        super().__init__(
            message="PDF file is corrupted or invalid",
            filename=filename
        )


class PDFTooLargeError(PDFProcessingError):
    """PDF file too large"""
    
    def __init__(self, filename: str, size_mb: float, max_size_mb: int = 100):
        super().__init__(
            message=f"PDF file exceeds maximum size of {max_size_mb}MB",
            filename=filename,
            details={"size_mb": size_mb, "max_size_mb": max_size_mb}
        )


# Authentication/Authorization exceptions (for future use)
class AuthenticationError(NSEXPException):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(NSEXPException):
    """Authorization error"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


# Rate limiting exceptions
class RateLimitExceededError(NSEXPException):
    """Rate limit exceeded"""
    
    def __init__(self, resource: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded for {resource}",
            code="RATE_LIMIT_EXCEEDED",
            details={"resource": resource, "retry_after_seconds": retry_after},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
