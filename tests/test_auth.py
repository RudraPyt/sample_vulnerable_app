"""Tests for authentication service in Sample Vulnerable App.

Contains passing tests for session creation and role permissions, and exactly ONE failing test
(test_verify_token_with_iso_utc_timestamp) that triggers the planted TypeError (naive vs. aware datetime).
"""

from datetime import datetime, timezone, timedelta
import pytest
import sys
from pathlib import Path

# Add project root to sys.path so services can be imported cleanly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.auth import (
    generate_session_payload,
    has_permission,
    verify_auth_token,
)


def test_generate_session_payload():
    """Verify session payload generation with user id and roles."""
    payload = generate_session_payload("user_123", ["editor"])
    assert payload["user_id"] == "user_123"
    assert "editor" in payload["roles"]
    assert "issued_at" in payload


def test_has_permission():
    """Verify role checks and admin override."""
    user_token = {"roles": ["viewer"]}
    admin_token = {"roles": ["admin"]}
    assert has_permission(user_token, "viewer") is True
    assert has_permission(user_token, "editor") is False
    assert has_permission(admin_token, "billing") is True


def test_verify_auth_token_missing_data():
    """Verify invalid or empty token data returns False without crashing."""
    assert verify_auth_token({}) is False
    assert verify_auth_token({"user_id": "u1"}) is False


def test_verify_token_with_iso_utc_timestamp():
    """PLANTED FAILING TEST: Triggers TypeError when comparing naive now with UTC-aware expires_at."""
    # Future timestamp with UTC offset (+00:00)
    future_utc = datetime.now(timezone.utc) + timedelta(hours=2)
    token_data = {
        "user_id": "user_456",
        "roles": ["user"],
        "expires_at": future_utc.isoformat(),  # e.g. "2026-10-21T01:30:00+00:00"
    }

    # Line 42 in services/auth.py compares datetime.now() (naive) > expires_at (aware)
    # raising TypeError: can't compare offset-naive and offset-aware datetimes
    is_valid = verify_auth_token(token_data)
    assert is_valid is True
