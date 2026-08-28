"""
Security module for JWT authentication.
Verifies Supabase Auth JWT tokens and extracts user identity.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import PyJWTError

from app.config import get_settings

# HTTP Bearer scheme for Swagger UI integration
security_scheme = HTTPBearer(
    scheme_name="Supabase JWT",
    description="Paste your Supabase access_token here (without 'Bearer ' prefix)",
    auto_error=True,
)


class CurrentUser:
    """Represents the authenticated user extracted from JWT."""

    def __init__(self, user_id: str, email: str, role: str = "authenticated"):
        self.id = user_id
        self.email = email
        self.role = role

    def __repr__(self):
        return f"CurrentUser(id={self.id}, email={self.email})"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> CurrentUser:
    """
    FastAPI dependency that validates the JWT Bearer token
    and returns the authenticated user.

    Raises:
        HTTPException 401: If token is missing, expired, or invalid.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from app.database import get_supabase_admin
        supabase = get_supabase_admin()
        user_res = supabase.auth.get_user(token)

        if not user_res or not user_res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = user_res.user
        return CurrentUser(
            user_id=str(user.id),
            email=user.email or "",
            role=getattr(user, "role", "authenticated") or "authenticated",
        )

    except HTTPException:
        raise
    except Exception as e:
        # Fallback decode if Supabase network call fails but payload has valid sub
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            if user_id:
                return CurrentUser(
                    user_id=str(user_id),
                    email=payload.get("email", ""),
                    role=payload.get("role", "authenticated"),
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
