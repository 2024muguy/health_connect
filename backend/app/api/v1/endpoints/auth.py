"""
HealthConnect AI - Authentication Endpoints
============================================
Authentication and authorization endpoints.

Endpoints:
- POST /auth/register: Register new user
- POST /auth/login: Login
- POST /auth/refresh: Refresh token
- POST /auth/logout: Logout
- GET /auth/me: Get current user
"""

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session
from app.database.session import get_session as get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import security_manager
from app.api.deps import get_current_user
from app.schemas.chat import ChatRequest  # For consistency

from pydantic import BaseModel, EmailStr, Field, validator

from config.settings import get_settings
from config.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


# ============================================
# Request/Response Schemas
# ============================================
class RegisterRequest(BaseModel):
    """Register request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=200)
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain number")
        return v


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response"""
    user_id: str
    email: str
    full_name: str
    roles: list = []


# ============================================
# Endpoints
# ============================================
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user (persists to SQLite or Neon Postgres).
    """
    from app.repositories.user_repository import UserRepository
    from app.core.security import hash_password

    repo = UserRepository(db)

    if repo.email_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = repo.create(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
    )

    access_token = security_manager.create_access_token(
        subject=user.id,
        extra_claims={"email": user.email, "roles": (user.roles or "user").split(",")},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = security_manager.create_refresh_token(
        subject=user.id,
        extra_claims={"email": user.email},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    logger.info(f"Registered new user: {user.email} ({user.id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user (verifies against database).
    """
    from app.repositories.user_repository import UserRepository
    from app.core.security import verify_password

    repo = UserRepository(db)
    user = repo.get_by_email(request.email)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )

    # Update last login
    repo.update_last_login(user)

    access_token = security_manager.create_access_token(
        subject=user.id,
        extra_claims={"email": user.email, "roles": (user.roles or "user").split(",")},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = security_manager.create_refresh_token(
        subject=user.id,
        extra_claims={"email": user.email},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    logger.info(f"User logged in: {user.email} ({user.id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token (verifies user still exists and is active).
    """
    from app.repositories.user_repository import UserRepository

    try:
        payload = security_manager.verify_token(request.refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists or is inactive",
        )

    access_token = security_manager.create_access_token(
        subject=user.id,
        extra_claims={"email": user.email, "roles": (user.roles or "user").split(",")},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token_new = security_manager.create_refresh_token(
        subject=user.id,
        extra_claims={"email": user.email},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_new,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user.
    """
    return {"status": "logged_out"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user information (from database).
    """
    from app.repositories.user_repository import UserRepository

    repo = UserRepository(db)
    user = repo.get_by_id(current_user.get("sub", ""))

    if not user:
        # Token is valid but user was deleted — fall back to token claims
        return UserResponse(
            user_id=current_user.get("sub", ""),
            email=current_user.get("email", ""),
            full_name=current_user.get("full_name", current_user.get("email", "")),
            roles=current_user.get("roles", ["user"]),
        )

    return UserResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=(user.roles or "user").split(","),
    )