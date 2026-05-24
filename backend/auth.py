"""
ResuMatch AI — Authentication Module
JWT-based auth with bcrypt password hashing. No external auth service needed.
Includes email verification flow.
"""

import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from database import (
    create_user, get_user_by_email, get_user_by_id,
    update_last_login, create_session, end_session, log_activity,
    verify_user_by_token, get_user_by_verification_token,
)
from mailer import send_verification_email, FRONTEND_URL

# ──────── Config ────────
SECRET_KEY = os.environ.get("JWT_SECRET", "resumatch-ai-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# ──────── Pydantic Models ────────

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: str
    last_login: Optional[str] = None


# ──────── JWT Helpers ────────

def create_token(user_id: int, role: str, session_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "sid": session_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ──────── Auth Dependencies ────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency that extracts and validates the current user from JWT."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = decode_token(credentials.credentials)
    user = get_user_by_id(int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")

    user["session_id"] = payload.get("sid")
    return user


async def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires admin role."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[dict]:
    """Optional auth - returns None if no token provided."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return get_user_by_id(payload["sub"])
    except Exception:
        return None


# ──────── Routes ────────

@router.post("/register")
async def register(req: RegisterRequest):
    """Create a new user account and send verification email."""
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")

    email = req.email.lower().strip()

    # Check if exists
    existing = get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash password
    pw_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)

    try:
        user = create_user(email, req.name.strip(), pw_hash, verification_token=verification_token, is_verified=0)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Send verification email
    send_verification_email(email, req.name.strip(), verification_token)

    log_activity(user["id"], "register", f"New account: {email} (pending verification)")

    return {
        "message": "Account created! Please check your email to verify your account.",
        "requires_verification": True,
        "user": {
            "id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]
        },
    }


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    """Authenticate and return JWT token."""
    email = req.email.lower().strip()
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(req.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")

    # Block login for unverified users
    if not user.get("is_verified", 0):
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in. Check your inbox for the verification link.",
        )

    # Create session
    ip = request.client.host if request.client else ""
    ua = request.headers.get("user-agent", "")[:200]
    session_id = create_session(user["id"], ip, ua)

    # Update last login
    update_last_login(user["id"])

    # Create JWT
    token = create_token(user["id"], user["role"], session_id)

    log_activity(user["id"], "login", f"Login from {ip}")

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
    }


@router.get("/verify")
async def verify_email(token: str = Query(..., description="Verification token from email")):
    """Verify user email and redirect to login page."""
    if not token or len(token) < 10:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    # Check if token exists
    user = get_user_by_verification_token(token)
    if not user:
        # Token not found or already verified — redirect with error
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?verification=expired",
            status_code=302,
        )

    # Mark user as verified
    success = verify_user_by_token(token)
    if not success:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?verification=failed",
            status_code=302,
        )

    log_activity(user["id"], "email_verified", f"Email verified: {user['email']}")

    # Redirect to frontend login page with success indicator
    return RedirectResponse(
        url=f"{FRONTEND_URL}/?verified=true",
        status_code=302,
    )


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """End the current session."""
    session_id = user.get("session_id")
    if session_id:
        end_session(session_id)

    log_activity(user["id"], "logout", "")

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }
