"""Authentication and token verification service for Sample Vulnerable App.

Implements JWT/session token validation with a planted offset-naive vs. offset-aware
datetime mismatch on line 42.
"""

from datetime import datetime, timezone
from typing import Any, Optional


def generate_session_payload(user_id: str, roles: Optional[list[str]] = None) -> dict[str, Any]:
    """Create session token metadata dictionary."""
    return {
        "user_id": user_id,
        "roles": roles or ["user"],
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }


def has_permission(token_data: dict[str, Any], required_role: str) -> bool:
    """Check if token possesses the required role."""
    roles = token_data.get("roles", [])
    return required_role in roles or "admin" in roles


def verify_auth_token(token_data: dict[str, Any]) -> bool:
    """Validate token payload and expiration timestamp.

    Planted bug: Line 42 compares a naive current datetime with an ISO-formatted
    timezone-aware UTC expiration datetime, raising TypeError: can't compare offset-naive
    and offset-aware datetimes when expires_at has UTC offset.
    """
    if not token_data or not isinstance(token_data, dict):
        return False

    raw_exp = token_data.get("expires_at")
    if not raw_exp:
        return False

    if isinstance(raw_exp, str):
        expires_at = datetime.fromisoformat(raw_exp)
    elif isinstance(raw_exp, datetime):
        expires_at = raw_exp
    else:
        return False

    # PLANTED BUG: datetime.now() produces a naive datetime (without timezone info).
    # When expires_at is timezone-aware (e.g. from datetime.now(timezone.utc)),
    # comparing naive > aware raises TypeError: can't compare offset-naive and offset-aware datetimes.
    now = datetime.now()
    if now > expires_at:
        return False

    return True
