"""Tests for envoy_cli.env_scope."""

import pytest

from envoy_cli.env_scope import (
    ScopeError,
    get_scopes,
    is_allowed,
    list_restricted_keys,
    remove_scope,
    set_scope,
)
from envoy_cli.vault import save_vault


PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "dev": {"DB_URL": "postgres://dev", "SECRET": "dev-secret"},
        "prod": {"DB_URL": "postgres://prod", "SECRET": "prod-secret"},
    }
    save_vault(path, PASSWORD, data)
    return path


def test_set_scope_returns_sorted_list(vault_file):
    result = set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod", "staging"])
    assert result == ["prod", "staging"]


def test_set_scope_persisted(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    scopes = get_scopes(vault_file, PASSWORD, "dev")
    assert scopes["SECRET"] == ["prod"]


def test_set_scope_deduplicates(vault_file):
    result = set_scope(vault_file, PASSWORD, "dev", "DB_URL", ["prod", "prod", "staging"])
    assert result == ["prod", "staging"]


def test_set_scope_unknown_profile_raises(vault_file):
    with pytest.raises(ScopeError, match="Profile"):
        set_scope(vault_file, PASSWORD, "ghost", "KEY", ["prod"])


def test_set_scope_unknown_key_raises(vault_file):
    with pytest.raises(ScopeError, match="Key"):
        set_scope(vault_file, PASSWORD, "dev", "MISSING", ["prod"])


def test_remove_scope_returns_true(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    assert remove_scope(vault_file, PASSWORD, "dev", "SECRET") is True


def test_remove_scope_not_found_returns_false(vault_file):
    assert remove_scope(vault_file, PASSWORD, "dev", "DB_URL") is False


def test_remove_scope_clears_restriction(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    remove_scope(vault_file, PASSWORD, "dev", "SECRET")
    scopes = get_scopes(vault_file, PASSWORD, "dev")
    assert "SECRET" not in scopes


def test_is_allowed_no_restriction(vault_file):
    assert is_allowed(vault_file, PASSWORD, "dev", "DB_URL", "prod") is True


def test_is_allowed_within_scope(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    assert is_allowed(vault_file, PASSWORD, "dev", "SECRET", "prod") is True


def test_is_allowed_outside_scope(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    assert is_allowed(vault_file, PASSWORD, "dev", "SECRET", "staging") is False


def test_list_restricted_keys(vault_file):
    set_scope(vault_file, PASSWORD, "dev", "SECRET", ["prod"])
    set_scope(vault_file, PASSWORD, "dev", "DB_URL", ["staging"])
    keys = list_restricted_keys(vault_file, PASSWORD, "dev")
    assert keys == ["DB_URL", "SECRET"]


def test_list_restricted_keys_empty(vault_file):
    assert list_restricted_keys(vault_file, PASSWORD, "dev") == []
