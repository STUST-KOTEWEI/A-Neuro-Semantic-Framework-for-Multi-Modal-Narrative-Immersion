"""Basic configuration and API key authentication utilities.

This lightweight module centralizes security related helpers (API Key) and
runtime feature toggles (future extension: load from env / secrets manager).
"""
from __future__ import annotations

import os
from fastapi import Header, HTTPException, status, Depends


# ---------------------------------------------------------------------------
# API Key Management
# ---------------------------------------------------------------------------
# In production you would NOT hardcode keys; instead populate via environment
# variables or a secure secret store. For demonstration we allow a comma
# separated list in MODERN_READER_API_KEYS.
RAW_KEYS = os.getenv("MODERN_READER_API_KEYS", "dev-key-123,example-key-abc")
API_KEYS = {k.strip() for k in RAW_KEYS.split(",") if k.strip()}


async def api_key_auth(x_api_key: str | None = Header(default=None)) -> str:
    """FastAPI dependency enforcing an API key via X-API-Key header.

    Raises 401 if header missing or invalid.
    Returns the accepted key (caller identity placeholder) otherwise.
    """
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    return x_api_key


ApiKeyDependency = Depends(api_key_auth)

__all__ = ["api_key_auth", "ApiKeyDependency", "API_KEYS"]
