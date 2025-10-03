"""
⚠️ DEPRECATED - NOT USED IN SIMPLIFIED SYSTEM ⚠️

Authentication and Authorization System
Specialized for neurosurgical practitioners and researchers

STATUS: This file is NOT USED in the current single-user simplified system.

The NSEXP system is designed as a single-user personal knowledge management
tool and does NOT require authentication. This file was part of a planned
multi-user system that was never implemented.

ISSUES:
1. Imports from non-existent 'schemas.auth' module
2. References User model that exists but is unused
3. Not imported by main_simplified.py
4. Adds unnecessary complexity

If you need authentication:
1. Create backend/schemas/auth.py with required Pydantic models
2. Update main_simplified.py to use auth middleware
3. Add user management endpoints
4. Test thoroughly

For now, this file should be archived or removed.
"""

# THESE IMPORTS WILL FAIL - schemas.auth doesn't exist
# from datetime import datetime, timedelta, timezone
# from typing import Optional, Union, Dict, Any
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# import logging

# from config.settings import settings
# from core.database import get_db
# from models.database import User, NeurosurgicalSpecialty
# from schemas.auth import TokenData, UserCreate, UserResponse  # MISSING MODULE

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class AuthenticationError(Exception):
    """Custom authentication exception"""
    pass


class AuthorizationError(Exception):
    """Custom authorization exception"""
    pass


class AuthService:
    """
    Handles authentication and authorization for neurosurgical users
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        # Query user
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()

        return user

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
        is_verified: bool = False
    ) -> User:
        """
        Create new user account
        """
        # Check if user exists
        existing_user = await db.execute(
            select(User).where(
                (User.email == user_data.email) | (User.username == user_data.username)
            )
        )

        if existing_user.scalar_one_or_none():
            raise ValueError("User with this email or username already exists")

        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=AuthService.get_password_hash(user_data.password),
            full_name=user_data.full_name,
            specialty=user_data.specialty,
            years_experience=user_data.years_experience,
            hospital=user_data.hospital,
            residency_program=user_data.residency_program,
            board_certified=user_data.board_certified,
            is_active=True,
            is_verified=is_verified,
            learning_preferences=user_data.learning_preferences or {}
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        logger.info(f"New user created: {db_user.email} (Specialty: {db_user.specialty})")

        return db_user

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """
        Get current authenticated user from JWT token
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "access":
                raise credentials_exception

            token_data = TokenData(user_id=user_id)

        except JWTError:
            raise credentials_exception

        # Get user from database
        result = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Verify user is active
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        return current_user

    @staticmethod
    async def get_current_superuser(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        Verify user is superuser (admin)
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user


class PermissionChecker:
    """
    Check user permissions for specific resources
    """

    def __init__(self, required_specialty: Optional[NeurosurgicalSpecialty] = None):
        self.required_specialty = required_specialty

    async def __call__(self, user: User = Depends(AuthService.get_current_active_user)) -> User:
        """
        Check if user has required specialty
        """
        if self.required_specialty and user.specialty != self.required_specialty:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This resource requires {self.required_specialty.value} specialty"
            )
        return user


class RoleChecker:
    """
    Role-based access control for neurosurgical system
    """

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(AuthService.get_current_active_user)) -> User:
        """
        Check if user has required role
        """
        user_roles = user.roles if hasattr(user, 'roles') else []

        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation"
            )
        return user


class ExperienceLevelChecker:
    """
    Check user's experience level for advanced features
    """

    def __init__(self, min_years: int = 0, require_board_certification: bool = False):
        self.min_years = min_years
        self.require_board_certification = require_board_certification

    async def __call__(self, user: User = Depends(AuthService.get_current_active_user)) -> User:
        """
        Check user's experience and certification
        """
        if user.years_experience is not None and user.years_experience < self.min_years:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires at least {self.min_years} years of experience"
            )

        if self.require_board_certification and not user.board_certified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature requires board certification"
            )

        return user


# Dependency shortcuts
get_current_user = AuthService.get_current_user
get_current_active_user = AuthService.get_current_active_user
get_current_superuser = AuthService.get_current_superuser

# Specialty-specific dependencies
require_tumor_specialty = PermissionChecker(NeurosurgicalSpecialty.TUMOR)
require_vascular_specialty = PermissionChecker(NeurosurgicalSpecialty.VASCULAR)
require_spine_specialty = PermissionChecker(NeurosurgicalSpecialty.SPINE)
require_functional_specialty = PermissionChecker(NeurosurgicalSpecialty.FUNCTIONAL)

# Experience-based dependencies
require_attending_level = ExperienceLevelChecker(min_years=5, require_board_certification=True)
require_fellow_level = ExperienceLevelChecker(min_years=4)
require_senior_resident = ExperienceLevelChecker(min_years=3)


class TokenService:
    """
    Manage JWT tokens and sessions
    """

    @staticmethod
    async def validate_refresh_token(token: str, db: AsyncSession) -> Optional[User]:
        """
        Validate refresh token and return user
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                return None

            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            return user if user and user.is_active else None

        except JWTError:
            return None

    @staticmethod
    def create_token_pair(user: User) -> Dict[str, str]:
        """
        Create access and refresh token pair
        """
        access_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "specialty": user.specialty.value if user.specialty else None
        }

        refresh_token_data = {"sub": str(user.id)}

        return {
            "access_token": AuthService.create_access_token(access_token_data),
            "refresh_token": AuthService.create_refresh_token(refresh_token_data),
            "token_type": "bearer"
        }


# Export for use in other modules
__all__ = [
    "AuthService",
    "TokenService",
    "PermissionChecker",
    "RoleChecker",
    "ExperienceLevelChecker",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "require_tumor_specialty",
    "require_vascular_specialty",
    "require_spine_specialty",
    "require_functional_specialty",
    "require_attending_level",
    "require_fellow_level",
    "require_senior_resident",
    "pwd_context"
]