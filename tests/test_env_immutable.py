"""Tests for envoy_cli.env_immutable."""

import pytest

from envoy_cli.env_immutable import (
    ImmutableError,
    check_immutable,
    get_immutable_keys,
    is_immutable,
    mark_immutable,
    unmark_immutable,
)
from envoy_cli.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    password = "secret"
    vault = {
        "profiles": {
            "dev": {"API_KEY": "abc123", "DEBUG": "true"},
            "prod": {"API_KEY": "xyz789"},
        }
    }
    save_vault(str(path), password, vault)
    return str(path), password


def test_get_immutable_keys_empty(vault_file):
    path, pw = vault_file
    keys = get_immutable_keys(path, pw, "dev")
    assert keys == []


def test_mark_immutable_returns_sorted_list(vault_file):
    path, pw = vault_file
    result = mark_immutable(path, pw, "dev", "API_KEY")
    assert result == ["API_KEY"]


def test_mark_immutable_persisted(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "DEBUG")
    keys = get_immutable_keys(path, pw, "dev")
    assert "DEBUG" in keys


def test_mark_multiple_keys_sorted(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "DEBUG")
    result = mark_immutable(path, pw, "dev", "API_KEY")
    assert result == ["API_KEY", "DEBUG"]


def test_mark_duplicate_no_duplicates(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "API_KEY")
    result = mark_immutable(path, pw, "dev", "API_KEY")
    assert result.count("API_KEY") == 1


def test_mark_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(ImmutableError, match="Profile 'staging' not found"):
        mark_immutable(path, pw, "staging", "API_KEY")


def test_mark_unknown_key_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(ImmutableError, match="Key 'MISSING'"):
        mark_immutable(path, pw, "dev", "MISSING")


def test_unmark_immutable_removes_key(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "API_KEY")
    result = unmark_immutable(path, pw, "dev", "API_KEY")
    assert "API_KEY" not in result


def test_unmark_nonexistent_key_is_noop(vault_file):
    path, pw = vault_file
    result = unmark_immutable(path, pw, "dev", "NONEXISTENT")
    assert result == []


def test_is_immutable_true(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "API_KEY")
    assert is_immutable(path, pw, "dev", "API_KEY") is True


def test_is_immutable_false(vault_file):
    path, pw = vault_file
    assert is_immutable(path, pw, "dev", "API_KEY") is False


def test_check_immutable_raises_when_immutable(vault_file):
    path, pw = vault_file
    mark_immutable(path, pw, "dev", "API_KEY")
    with pytest.raises(ImmutableError, match="immutable and cannot be modified"):
        check_immutable(path, pw, "dev", "API_KEY")


def test_check_immutable_passes_when_not_immutable(vault_file):
    path, pw = vault_file
    # Should not raise
    check_immutable(path, pw, "dev", "API_KEY")
