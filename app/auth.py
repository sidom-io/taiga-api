"""
Authentication and session management.

This module provides in-memory session storage for Taiga auth tokens
and middleware for request validation.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class SessionStore:
    """
    In-memory session store for auth tokens.

    Stores tokens with expiration time. Does not persist across server restarts.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, any]] = {}

    def set_token(self, token: str, ttl_seconds: int = 82800) -> None:
        """
        Store a token with expiration time.

        Args:
            token: The Taiga auth token
            ttl_seconds: Time to live in seconds (default: ~23 hours)
        """
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self._sessions["current"] = {
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
        }

    def get_token(self) -> Optional[str]:
        """
        Get the current valid token.

        Returns:
            The token if valid and not expired, None otherwise
        """
        session = self._sessions.get("current")
        if not session:
            return None

        # Check if expired
        if datetime.utcnow() > session["expires_at"]:
            # Clean up expired token
            del self._sessions["current"]
            return None

        return session["token"]

    def has_valid_token(self) -> bool:
        """
        Check if there's a valid token in the session.

        Returns:
            True if valid token exists, False otherwise
        """
        return self.get_token() is not None

    def get_token_info(self) -> Optional[Dict[str, any]]:
        """
        Get token metadata.

        Returns:
            Dict with token info (without the actual token value) or None
        """
        session = self._sessions.get("current")
        if not session:
            return None

        is_valid = datetime.utcnow() <= session["expires_at"]
        time_remaining = None
        if is_valid:
            time_remaining = int((session["expires_at"] - datetime.utcnow()).total_seconds())

        return {
            "is_valid": is_valid,
            "created_at": session["created_at"].isoformat(),
            "expires_at": session["expires_at"].isoformat(),
            "time_remaining_seconds": time_remaining,
        }

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()


# Global session store instance
session_store = SessionStore()


# Security scheme for bearer token
security = HTTPBearer(auto_error=False)


async def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> str:
    """
    Dependency that requires authentication.

    Checks for valid token in session store.
    Raises HTTPException if no valid token.

    Args:
        request: The FastAPI request object
        credentials: Optional bearer token credentials (not used, token comes from session)

    Returns:
        The valid token

    Raises:
        HTTPException: If no valid token in session
    """
    token = session_store.get_token()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "No valid authentication token",
                "message": "Please set your Taiga auth token via POST /auth",
                "instructions": "You can get your token from Taiga by: "
                "1. Log in to Taiga, 2. Open browser DevTools (F12), "
                "3. Go to Application/Storage > Cookies, "
                "4. Copy the 'auth-token' cookie value",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


def get_optional_auth() -> Optional[str]:
    """
    Get auth token if available, but don't raise exception if missing.

    Returns:
        The token if available, None otherwise
    """
    return session_store.get_token()
