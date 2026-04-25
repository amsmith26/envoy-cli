"""Tests for envoy_cli.env_readonly."""
import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_readonly import (
    ReadonlyError,
    get_readonly_keys,
    mark_readonly,
    unmark_readonly,
    is_readonly,
    assert_not_readonly,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "profiles": {
            "dev": {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"},
        }
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_get_readonly_keys_empty(vault_file):
    keys = get_readonly_keys(vault_file, PASSWORD, "dev")
    assert keys == []


def test_mark_readonly_returns_sorted_list(vault_file):
    result = mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    assert result == ["API_KEY"]


def test_mark_readonly_persisted(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    keys = get_readonly_keys(vault_file, PASSWORD, "dev")
    assert "API_KEY" in keys


def test_mark_multiple_keys_sorted(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "PORT")
    mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    keys = get_readonly_keys(vault_file, PASSWORD, "dev")
    assert keys == ["API_KEY", "PORT"]


def test_mark_duplicate_no_duplicates(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "DEBUG")
    mark_readonly(vault_file, PASSWORD, "dev", "DEBUG")
    keys = get_readonly_keys(vault_file, PASSWORD, "dev")
    assert keys.count("DEBUG") == 1


def test_mark_readonly_unknown_profile_raises(vault_file):
    with pytest.raises(ReadonlyError, match="Profile"):
        mark_readonly(vault_file, PASSWORD, "prod", "API_KEY")


def test_mark_readonly_unknown_key_raises(vault_file):
    with pytest.raises(ReadonlyError, match="Key"):
        mark_readonly(vault_file, PASSWORD, "dev", "NONEXISTENT")


def test_unmark_readonly_removes_key(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    remaining = unmark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    assert "API_KEY" not in remaining


def test_unmark_not_protected_raises(vault_file):
    with pytest.raises(ReadonlyError, match="not marked read-only"):
        unmark_readonly(vault_file, PASSWORD, "dev", "PORT")


def test_is_readonly_true(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    assert is_readonly(vault_file, PASSWORD, "dev", "API_KEY") is True


def test_is_readonly_false(vault_file):
    assert is_readonly(vault_file, PASSWORD, "dev", "DEBUG") is False


def test_assert_not_readonly_raises_when_protected(vault_file):
    mark_readonly(vault_file, PASSWORD, "dev", "API_KEY")
    with pytest.raises(ReadonlyError, match="read-only"):
        assert_not_readonly(vault_file, PASSWORD, "dev", "API_KEY")


def test_assert_not_readonly_passes_when_unprotected(vault_file):
    # Should not raise
    assert_not_readonly(vault_file, PASSWORD, "dev", "PORT")
