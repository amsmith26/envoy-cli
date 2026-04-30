"""Tests for envoy_cli.env_ttl."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

import pytest

from envoy_cli.env_ttl import (
    TTLError,
    get_ttl,
    is_expired,
    list_ttls,
    purge_expired,
    remove_ttl,
    set_ttl,
)
from envoy_cli.vault import save_vault

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, PASSWORD, {"dev": {"API_KEY": "abc", "DB_URL": "postgres://"}})
    return path


def test_set_ttl_returns_expiry_string(vault_file):
    expiry = set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 3600)
    assert "T" in expiry
    assert expiry.endswith("Z")


def test_set_ttl_persisted(vault_file):
    set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 3600)
    expiry = get_ttl(vault_file, PASSWORD, "dev", "API_KEY")
    assert expiry is not None


def test_get_ttl_missing_returns_none(vault_file):
    result = get_ttl(vault_file, PASSWORD, "dev", "API_KEY")
    assert result is None


def test_set_ttl_unknown_profile_raises(vault_file):
    with pytest.raises(TTLError, match="Profile"):
        set_ttl(vault_file, PASSWORD, "prod", "API_KEY", 60)


def test_set_ttl_unknown_key_raises(vault_file):
    with pytest.raises(TTLError, match="Key"):
        set_ttl(vault_file, PASSWORD, "dev", "MISSING_KEY", 60)


def test_set_ttl_zero_seconds_raises(vault_file):
    with pytest.raises(TTLError, match="positive"):
        set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 0)


def test_is_expired_false_for_future(vault_file):
    set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 3600)
    assert is_expired(vault_file, PASSWORD, "dev", "API_KEY") is False


def test_is_expired_true_for_past(vault_file):
    future = datetime.now(timezone.utc) - timedelta(seconds=1)
    expiry_str = future.strftime("%Y-%m-%dT%H:%M:%SZ")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, PASSWORD)
    vault.setdefault("__ttl__", {}).setdefault("dev", {})["API_KEY"] = expiry_str
    from envoy_cli.vault import save_vault
    save_vault(vault_file, PASSWORD, vault)
    assert is_expired(vault_file, PASSWORD, "dev", "API_KEY") is True


def test_is_expired_no_ttl_returns_false(vault_file):
    assert is_expired(vault_file, PASSWORD, "dev", "API_KEY") is False


def test_remove_ttl_returns_true_when_removed(vault_file):
    set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 3600)
    assert remove_ttl(vault_file, PASSWORD, "dev", "API_KEY") is True
    assert get_ttl(vault_file, PASSWORD, "dev", "API_KEY") is None


def test_remove_ttl_returns_false_when_not_set(vault_file):
    assert remove_ttl(vault_file, PASSWORD, "dev", "API_KEY") is False


def test_list_ttls_empty(vault_file):
    assert list_ttls(vault_file, PASSWORD, "dev") == {}


def test_list_ttls_sorted(vault_file):
    set_ttl(vault_file, PASSWORD, "dev", "DB_URL", 100)
    set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 200)
    result = list_ttls(vault_file, PASSWORD, "dev")
    assert list(result.keys()) == ["API_KEY", "DB_URL"]


def test_purge_expired_removes_past_keys(vault_file):
    from envoy_cli.vault import load_vault, save_vault
    past = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    vault = load_vault(vault_file, PASSWORD)
    vault.setdefault("__ttl__", {}).setdefault("dev", {})["API_KEY"] = past
    save_vault(vault_file, PASSWORD, vault)
    removed = purge_expired(vault_file, PASSWORD, "dev")
    assert "API_KEY" in removed


def test_purge_expired_leaves_future_keys(vault_file):
    set_ttl(vault_file, PASSWORD, "dev", "API_KEY", 3600)
    removed = purge_expired(vault_file, PASSWORD, "dev")
    assert "API_KEY" not in removed


def test_purge_expired_unknown_profile_raises(vault_file):
    with pytest.raises(TTLError, match="Profile"):
        purge_expired(vault_file, PASSWORD, "ghost")
