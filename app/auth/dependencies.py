"""FastAPI dependency for Supabase JWT verification."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwks import verify_supabase_token
from app.config import Settings, get_settings

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Extract and verify Supabase JWT from Authorization header.

    Returns decoded token payload with 'sub' (user_id), 'email', etc.
    """
    if not settings.supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth not configured",
        )

    try:
        return verify_supabase_token(
            credentials.credentials,
            settings.jwks_url,
            settings.supabase_url,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
