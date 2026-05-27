"""Supabase JWKS client with local caching."""

import time

import jwt
from jwt import PyJWKClient

_jwk_client: PyJWKClient | None = None
_jwk_client_loaded_at: float = 0
_JWKS_CACHE_TTL = 3600  # 1 hour


def get_jwk_client(jwks_url: str) -> PyJWKClient:
    """Get or refresh the JWKS client."""
    global _jwk_client, _jwk_client_loaded_at

    if _jwk_client and (time.time() - _jwk_client_loaded_at) < _JWKS_CACHE_TTL:
        return _jwk_client

    _jwk_client = PyJWKClient(jwks_url, cache_keys=True)
    _jwk_client_loaded_at = time.time()
    return _jwk_client


def verify_supabase_token(token: str, jwks_url: str, supabase_url: str) -> dict:
    """Verify a Supabase JWT using cached JWKS public key.

    Returns the decoded payload (contains 'sub' = user_id, 'email', etc.).
    Raises jwt.InvalidTokenError on failure.
    """
    jwk_client = get_jwk_client(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["HS256"],
        audience="authenticated",
        issuer=f"{supabase_url}/auth/v1",
    )
