"""
Authentication Service
======================

Utilities for password hashing, JWT tokens, and MFA.
"""

import io
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pyotp
import qrcode
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.user import Base, User

# Configuration
SECRET_KEY = os.environ.get("NEXUS_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup - users stored in app data directory
APP_DATA_DIR = Path.home() / ".nexus"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_DB_PATH = APP_DATA_DIR / "users.db"

engine = create_engine(f"sqlite:///{USERS_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Caller responsible for closing


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT utilities
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# MFA utilities
def generate_mfa_secret() -> str:
    """Generate a new TOTP secret."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "Nexus") -> str:
    """Get the TOTP provisioning URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code(uri: str) -> bytes:
    """Generate a QR code image for the TOTP URI."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


# User operations
def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, username: str, password: str, full_name: str | None = None) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email_or_username: str, password: str) -> User | None:
    """Authenticate a user by email/username and password."""
    # Try email first
    user = get_user_by_email(db, email_or_username)
    if not user:
        # Try username
        user = get_user_by_username(db, email_or_username)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def update_user_last_login(db: Session, user: User) -> None:
    """Update user's last login timestamp."""
    user.last_login = datetime.utcnow()
    db.commit()


def enable_mfa(db: Session, user: User, secret: str) -> None:
    """Enable MFA for a user."""
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.commit()


def disable_mfa(db: Session, user: User) -> None:
    """Disable MFA for a user."""
    user.mfa_secret = None
    user.mfa_enabled = False
    db.commit()


def update_user_profile(
    db: Session,
    user: User,
    full_name: str | None = None,
    bio: str | None = None,
    avatar_url: str | None = None,
) -> User:
    """Update user profile information."""
    if full_name is not None:
        user.full_name = full_name
    if bio is not None:
        user.bio = bio
    if avatar_url is not None:
        user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user


def update_user_settings(db: Session, user: User, settings: str) -> User:
    """Update user settings (JSON string)."""
    user.settings = settings
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, new_password: str) -> None:
    """Change user's password."""
    user.hashed_password = get_password_hash(new_password)
    db.commit()
