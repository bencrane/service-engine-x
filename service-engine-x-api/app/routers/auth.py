"""Auth API router — login and session management."""

from typing import Any

import bcrypt as bcrypt_lib
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.auth.dependencies import AuthContext, get_current_user
from app.auth.jwt import create_access_token
from app.database import get_supabase

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response with JWT token and user info."""

    token: str
    token_type: str = "bearer"
    expires_in_hours: int
    user: dict[str, Any]


class MeResponse(BaseModel):
    """Current user profile response."""

    id: str
    email: str
    name_f: str
    name_l: str
    name: str
    company: str | None
    phone: str | None
    org_id: str
    org_name: str | None
    role_id: str
    role_name: str | None
    status: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    """
    Authenticate a user with email and password.

    Returns a JWT token for use in subsequent API requests.
    The token should be sent as: Authorization: Bearer <token>
    """
    supabase = get_supabase()

    # Look up user by email (case-insensitive)
    result = (
        supabase.table("users")
        .select("id, email, password_hash, name_f, name_l, company, phone, org_id, role_id, status")
        .ilike("email", body.email.lower().strip())
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = result.data[0]

    # Check account is active
    if user.get("status", 0) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Verify password
    password_hash = user.get("password_hash")
    if not password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    try:
        password_valid = bcrypt_lib.checkpw(
            body.password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        # Invalid hash format in DB — treat as auth failure
        password_valid = False

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Fetch org name for response
    org_name = None
    org_result = (
        supabase.table("organizations")
        .select("name")
        .eq("id", user["org_id"])
        .execute()
    )
    if org_result.data:
        org_name = org_result.data[0]["name"]

    # Fetch role name for response
    role_name = None
    role_result = (
        supabase.table("roles")
        .select("name")
        .eq("id", user["role_id"])
        .execute()
    )
    if role_result.data:
        role_name = role_result.data[0]["name"]

    # Create JWT
    from app.config import get_settings

    settings = get_settings()

    token = create_access_token(
        user_id=user["id"],
        org_id=user["org_id"],
        role_id=user["role_id"],
    )

    return LoginResponse(
        token=token,
        token_type="bearer",
        expires_in_hours=settings.jwt_expiration_hours,
        user={
            "id": user["id"],
            "email": user["email"],
            "name_f": user["name_f"],
            "name_l": user["name_l"],
            "name": f"{user['name_f']} {user['name_l']}".strip(),
            "company": user.get("company"),
            "phone": user.get("phone"),
            "org_id": user["org_id"],
            "org_name": org_name,
            "role_id": user["role_id"],
            "role_name": role_name,
        },
    )


@router.get("/me", response_model=MeResponse)
async def me(auth: AuthContext = Depends(get_current_user)) -> MeResponse:
    """
    Get the current authenticated user's profile.

    Requires a valid JWT session token (not an API token).
    """
    supabase = get_supabase()

    result = (
        supabase.table("users")
        .select("id, email, name_f, name_l, company, phone, org_id, role_id, status")
        .eq("id", auth.user_id)
        .execute()
    )

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = result.data[0]

    # Fetch org name
    org_name = None
    org_result = (
        supabase.table("organizations")
        .select("name")
        .eq("id", user["org_id"])
        .execute()
    )
    if org_result.data:
        org_name = org_result.data[0]["name"]

    # Fetch role name
    role_name = None
    role_result = (
        supabase.table("roles")
        .select("name")
        .eq("id", user["role_id"])
        .execute()
    )
    if role_result.data:
        role_name = role_result.data[0]["name"]

    return MeResponse(
        id=user["id"],
        email=user["email"],
        name_f=user["name_f"],
        name_l=user["name_l"],
        name=f"{user['name_f']} {user['name_l']}".strip(),
        company=user.get("company"),
        phone=user.get("phone"),
        org_id=user["org_id"],
        org_name=org_name,
        role_id=user["role_id"],
        role_name=role_name,
        status=user.get("status", 1),
    )
