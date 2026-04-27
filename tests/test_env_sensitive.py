"""Tests for envoy_cli.env_sensitive."""

import pytest

from envoy_cli.env_sensitive import (
    SensitiveError,
    get_sensitive_keys,
    is_sensitive,
    mark_sensitive,
    redact_sensitive,
    unmark_sensitive,
)
from envoy_cli.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "profiles": {
            "prod": {
                "DB_PASS": "secret",
                "API_KEY": "abc123",
                "APP_NAME": "myapp",
            }
        }
    }
    save_vault(str(path), "pw", vault)
    return str(path)


def test_get_sensitive_keys_empty(vault_file):
    keys = get_sensitive_keys(vault_file, "pw", "prod")
    assert keys == []


def test_mark_sensitive_returns_sorted_list(vault_file):
    result = mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    assert result == ["DB_PASS"]


def test_mark_sensitive_persisted(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "API_KEY")
    keys = get_sensitive_keys(vault_file, "pw", "prod")
    assert "API_KEY" in keys


def test_mark_multiple_keys_sorted(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    result = mark_sensitive(vault_file, "pw", "prod", "API_KEY")
    assert result == ["API_KEY", "DB_PASS"]


def test_mark_duplicate_no_duplicates(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    result = mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    assert result.count("DB_PASS") == 1


def test_mark_sensitive_unknown_profile_raises(vault_file):
    with pytest.raises(SensitiveError, match="Profile"):
        mark_sensitive(vault_file, "pw", "staging", "DB_PASS")


def test_mark_sensitive_unknown_key_raises(vault_file):
    with pytest.raises(SensitiveError, match="Key"):
        mark_sensitive(vault_file, "pw", "prod", "NONEXISTENT")


def test_unmark_sensitive_removes_key(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    result = unmark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    assert "DB_PASS" not in result


def test_unmark_nonexistent_key_is_noop(vault_file):
    result = unmark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    assert result == []


def test_is_sensitive_true(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "API_KEY")
    assert is_sensitive(vault_file, "pw", "prod", "API_KEY") is True


def test_is_sensitive_false(vault_file):
    assert is_sensitive(vault_file, "pw", "prod", "APP_NAME") is False


def test_redact_sensitive_replaces_values(vault_file):
    mark_sensitive(vault_file, "pw", "prod", "DB_PASS")
    env = {"DB_PASS": "secret", "APP_NAME": "myapp"}
    redacted = redact_sensitive(vault_file, "pw", "prod", env)
    assert redacted["DB_PASS"] == "***REDACTED***"
    assert redacted["APP_NAME"] == "myapp"


def test_redact_sensitive_no_sensitive_keys(vault_file):
    env = {"DB_PASS": "secret", "APP_NAME": "myapp"}
    redacted = redact_sensitive(vault_file, "pw", "prod", env)
    assert redacted == env
