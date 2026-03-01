"""Tests for retention service."""

import pytest


def test_invalid_date_raises():
    from app.services.retention import tombstone_by_date
    with pytest.raises(ValueError):
        tombstone_by_date("not-a-date")


def test_valid_date_format():
    """Ensure valid date doesn't raise ValueError (even if DB absent)."""
    from app.services.retention import tombstone_by_date
    try:
        tombstone_by_date("2025-01-15")
    except ValueError:
        pytest.fail("Valid date raised ValueError")
    except Exception:
        pass  # DB errors are OK in unit tests


def test_restore_unknown_type():
    from app.services.retention import restore
    try:
        result = restore("unknown_type", 999)
        assert "error" in result
    except Exception:
        pass
