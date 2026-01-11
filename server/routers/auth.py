"""
Authentication Router
=====================

API endpoints for user authentication, registration, and profile management.
"""

import base64
import json
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    change_password,
    create_access_token,
    create_user,
    decode_token,
    disable_mfa,
    enable_mfa,
    generate_mfa_secret,
    generate_qr_code,
    get_db,
    get_totp_uri,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user_last_login,
    update_user_profile,
    update_user_settings,
    verify_password,
    verify_totp,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


# ============================================================================
# Request/Response Schemas
# ============================================================================


class UserRegister(BaseModel):
    """Registration request."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    password: str = Field(..., min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    """Login request."""
    email_or_username: str
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: "UserResponse"


class UserResponse(BaseModel):
    """User information response."""
    id: int
    email: str
    username: str
    full_name: str | None
    avatar_url: str | None
    bio: str | None
    mfa_enabled: bool
    created_at: str
    last_login: str | None
    settings: dict


class UserProfileUpdate(BaseModel):
    """Profile update request."""
    full_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class MFASetupResponse(BaseModel):
    """MFA setup response."""
    secret: str
    qr_code: str  # Base64 encoded PNG


class MFAVerify(BaseModel):
    """MFA verification request."""
    code: str = Field(..., min_length=6, max_length=6)


class MFAEnableRequest(BaseModel):
    """MFA enable request (verify with code)."""
    secret: str
    code: str = Field(..., min_length=6, max_length=6)


class SettingsUpdate(BaseModel):
    """Settings update request."""
    settings: dict


# ============================================================================
# Dependency: Get Current User
# ============================================================================


async def get_current_user_id(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> int:
    """Get the current authenticated user ID from JWT token."""
    token = credentials.credentials

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)


def get_user_or_404(db: Session, user_id: int):
    """Get user by ID or raise 404."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return user


def user_to_response(user) -> UserResponse:
    """Convert User model to response schema."""
    try:
        settings = json.loads(user.settings or "{}")
    except json.JSONDecodeError:
        settings = {}

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login=user.last_login.isoformat() if user.last_login else None,
        settings=settings,
    )


# ============================================================================
# Public Endpoints
# ============================================================================


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister):
    """Register a new user."""
    db = get_db()
    try:
        # Check if email already exists
        if get_user_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        # Check if username already exists
        if get_user_by_username(db, data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        # Create user
        user = create_user(
            db,
            email=data.email,
            username=data.username,
            password=data.password,
            full_name=data.full_name,
        )

        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return TokenResponse(
            access_token=access_token,
            user=user_to_response(user),
        )
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login with email/username and password."""
    db = get_db()
    try:
        user = authenticate_user(db, data.email_or_username, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        # Check MFA if enabled
        if user.mfa_enabled:
            if not data.mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA code required",
                    headers={"X-MFA-Required": "true"},
                )

            if not verify_totp(user.mfa_secret, data.mfa_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )

        # Update last login
        update_user_last_login(db, user)

        # Generate token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return TokenResponse(
            access_token=access_token,
            user=user_to_response(user),
        )
    finally:
        db.close()


# ============================================================================
# Protected Endpoints
# ============================================================================


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: int = Depends(get_current_user_id)):
    """Get current user's profile."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        return user_to_response(user)
    finally:
        db.close()


@router.patch("/me", response_model=UserResponse)
async def update_me(data: UserProfileUpdate, user_id: int = Depends(get_current_user_id)):
    """Update current user's profile."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        user = update_user_profile(
            db,
            user,
            full_name=data.full_name,
            bio=data.bio,
            avatar_url=data.avatar_url,
        )
        return user_to_response(user)
    finally:
        db.close()


@router.post("/change-password")
async def change_user_password(data: PasswordChange, user_id: int = Depends(get_current_user_id)):
    """Change current user's password."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        # Verify current password
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        change_password(db, user, data.new_password)
        return {"success": True, "message": "Password changed successfully"}
    finally:
        db.close()


@router.patch("/settings", response_model=UserResponse)
async def update_user_settings_endpoint(data: SettingsUpdate, user_id: int = Depends(get_current_user_id)):
    """Update current user's settings."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        user = update_user_settings(db, user, json.dumps(data.settings))
        return user_to_response(user)
    finally:
        db.close()


# ============================================================================
# MFA Endpoints
# ============================================================================


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(user_id: int = Depends(get_current_user_id)):
    """Generate MFA setup data (secret and QR code)."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled",
            )

        secret = generate_mfa_secret()
        uri = get_totp_uri(secret, user.email)
        qr_code = generate_qr_code(uri)
        qr_code_base64 = base64.b64encode(qr_code).decode("utf-8")

        return MFASetupResponse(
            secret=secret,
            qr_code=f"data:image/png;base64,{qr_code_base64}",
        )
    finally:
        db.close()


@router.post("/mfa/enable")
async def enable_mfa_endpoint(data: MFAEnableRequest, user_id: int = Depends(get_current_user_id)):
    """Enable MFA after verifying the code."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled",
            )

        # Verify the code matches the secret
        if not verify_totp(data.secret, data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code",
            )

        enable_mfa(db, user, data.secret)
        return {"success": True, "message": "MFA enabled successfully"}
    finally:
        db.close()


@router.post("/mfa/disable")
async def disable_mfa_endpoint(data: MFAVerify, user_id: int = Depends(get_current_user_id)):
    """Disable MFA (requires valid code)."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        if not user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled",
            )

        # Verify the code
        if not verify_totp(user.mfa_secret, data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code",
            )

        disable_mfa(db, user)
        return {"success": True, "message": "MFA disabled successfully"}
    finally:
        db.close()


@router.post("/mfa/verify")
async def verify_mfa_code(data: MFAVerify, user_id: int = Depends(get_current_user_id)):
    """Verify an MFA code (for testing)."""
    db = get_db()
    try:
        user = get_user_or_404(db, user_id)
        if not user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled",
            )

        is_valid = verify_totp(user.mfa_secret, data.code)
        return {"valid": is_valid}
    finally:
        db.close()
