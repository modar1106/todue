from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_supabase_admin
from app.models import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthResponse,
    ErrorResponse,
    UserProfile,
)
from app.security import CurrentUser, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    summary="Register a new user",
)
async def register(body: AuthRegisterRequest):
    """
    Register a new user with email and password.
    Automatically creates user and confirms email via admin client for instant session access.
    """
    try:
        supabase = get_supabase_admin()
        full_name = body.full_name or body.email.split("@")[0]

        # 1. Use Supabase Admin to create confirmed user directly
        try:
            admin_res = supabase.auth.admin.create_user(
                {
                    "email": body.email,
                    "password": body.password,
                    "email_confirm": True,
                    "user_metadata": {
                        "full_name": full_name,
                    },
                }
            )
            created_user = admin_res.user
        except Exception as admin_err:
            err_msg = str(admin_err).lower()
            if "already registered" in err_msg or "already in use" in err_msg or "unique" in err_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already registered. Please log in instead.",
                )
            # Fallback to standard sign_up if admin.create_user fails
            auth_response = supabase.auth.sign_up(
                {
                    "email": body.email,
                    "password": body.password,
                    "options": {
                        "data": {
                            "full_name": full_name,
                        }
                    },
                }
            )
            created_user = auth_response.user

        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Please check your email and password.",
            )

        # 2. Sign in to obtain session tokens
        try:
            login_res = supabase.auth.sign_in_with_password(
                {"email": body.email, "password": body.password}
            )
            if login_res.session and login_res.user:
                user = login_res.user
                session = login_res.session
                return AuthResponse(
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    token_type="bearer",
                    expires_in=session.expires_in or 3600,
                    user=UserProfile(
                        id=str(user.id),
                        email=user.email or "",
                        full_name=user.user_metadata.get("full_name", full_name),
                        avatar_url=user.user_metadata.get("avatar_url"),
                        role="user",
                        created_at=str(user.created_at) if user.created_at else None,
                    ),
                )
        except Exception:
            pass

        # Fallback response using created_user metadata
        return AuthResponse(
            access_token="session-pending",
            refresh_token="",
            token_type="bearer",
            expires_in=3600,
            user=UserProfile(
                id=str(created_user.id),
                email=created_user.email or "",
                full_name=created_user.user_metadata.get("full_name", full_name) if hasattr(created_user, 'user_metadata') and created_user.user_metadata else full_name,
                role="user",
                created_at=str(created_user.created_at) if hasattr(created_user, 'created_at') and created_user.created_at else None,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        err_str = str(e)
        if "already registered" in err_str.lower():
            detail = "Email is already registered. Please log in instead."
        else:
            detail = f"Registration failed: {err_str}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Login with email and password",
)
async def login(body: AuthLoginRequest):
    """
    Authenticate user and return JWT session tokens.
    """
    try:
        supabase = get_supabase_admin()

        auth_response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        user = auth_response.user
        session = auth_response.session

        # Fetch profile from public.users for the role field
        role = "user"
        try:
            profile_result = (
                supabase.table("users")
                .select("role")
                .eq("id", str(user.id))
                .execute()
            )
            if profile_result.data:
                role = profile_result.data[0].get("role", "user")
        except Exception:
            pass

        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user=UserProfile(
                id=str(user.id),
                email=user.email or "",
                full_name=user.user_metadata.get("full_name", ""),
                avatar_url=user.user_metadata.get("avatar_url"),
                role=role,
                created_at=str(user.created_at) if user.created_at else None,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        err_msg = str(e).lower()
        if "invalid" in err_msg or "credentials" in err_msg:
            detail = "Invalid email or password."
        elif "email not confirmed" in err_msg:
            detail = "Email is not confirmed yet. Please check your inbox or sign up again."
        else:
            detail = f"Login failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.
    """
    try:
        supabase = get_supabase_admin()

        result = (
            supabase.table("users")
            .select("*")
            .eq("id", current_user.id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found.",
            )

        profile = result.data[0]

        return UserProfile(
            id=profile["id"],
            email=profile["email"],
            full_name=profile.get("full_name"),
            avatar_url=profile.get("avatar_url"),
            role=profile.get("role", "user"),
            created_at=profile.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}",
        )
