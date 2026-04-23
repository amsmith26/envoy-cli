"""Tests for envoy_cli.env_expire."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from envoy_cli.env_expire import (
    ExpireError,
    get_expiry,
    list_all_expiries,
    list_expired,
    remove_expiry,
    set_expiry,
)
from envoy_cli.vault import save_vault

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "production": {"API_KEY": "abc123", "DB_URL": "postgres://localhost/db"},
        "staging": {"API_KEY": "staging-key"},
    }
    save_vault(path, PASSWORD, vault)
    return path


def _future(days: int = 1) -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=days)


def test_set_expiry_returns_formatted_string(vault_file):
    dt = _future()
    result = set_expiry(vault_file, PASSWORD, "production", "API_KEY", dt)
    assert result == dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_get_expiry_after_set(vault_file):
    dt = _future(5)
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", dt)
    retrieved = get_expiry(vault_file, PASSWORD, "production", "API_KEY")
    assert retrieved == dt


def test_get_expiry_not_set_returns_none(vault_file):
    result = get_expiry(vault_file, PASSWORD, "production", "API_KEY")
    assert result is None


def test_set_expiry_unknown_profile_raises(vault_file):
    with pytest.raises(ExpireError, match="Profile 'ghost'"):
        set_expiry(vault_file, PASSWORD, "ghost", "API_KEY", _future())


def test_set_expiry_unknown_key_raises(vault_file):
    with pytest.raises(ExpireError, match="Key 'MISSING'"):
        set_expiry(vault_file, PASSWORD, "production", "MISSING", _future())


def test_remove_expiry_returns_true(vault_file):
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", _future())
    assert remove_expiry(vault_file, PASSWORD, "production", "API_KEY") is True


def test_remove_expiry_not_set_returns_false(vault_file):
    assert remove_expiry(vault_file, PASSWORD, "production", "API_KEY") is False


def test_remove_expiry_clears_get(vault_file):
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", _future())
    remove_expiry(vault_file, PASSWORD, "production", "API_KEY")
    assert get_expiry(vault_file, PASSWORD, "production", "API_KEY") is None


def test_list_expired_includes_past_key(vault_file):
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", _past())
    expired = list_expired(vault_file, PASSWORD, "production")
    assert "API_KEY" in expired


def test_list_expired_excludes_future_key(vault_file):
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", _future())
    expired = list_expired(vault_file, PASSWORD, "production")
    assert "API_KEY" not in expired


def test_list_expired_empty_when_none_set(vault_file):
    assert list_expired(vault_file, PASSWORD, "production") == []


def test_list_all_expiries_returns_mapping(vault_file):
    dt1 = _future(3)
    dt2 = _future(7)
    set_expiry(vault_file, PASSWORD, "production", "API_KEY", dt1)
    set_expiry(vault_file, PASSWORD, "production", "DB_URL", dt2)
    entries = list_all_expiries(vault_file, PASSWORD, "production")
    assert "API_KEY" in entries
    assert "DB_URL" in entries
    assert len(entries) == 2


def test_list_all_expiries_empty(vault_file):
    assert list_all_expiries(vault_file, PASSWORD, "production") == {}
