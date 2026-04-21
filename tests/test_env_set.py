"""Unit tests for envoy_cli.env_set."""

import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.env_set import set_key, unset_key, get_key, list_keys, EnvSetError

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.env.vault"
    save_vault(str(path), PASSWORD, {"staging": {"FOO": "bar"}})
    return str(path)


def test_set_key_creates_entry(vault_file):
    set_key(vault_file, PASSWORD, "staging", "NEW_KEY", "hello")
    value = get_key(vault_file, PASSWORD, "staging", "NEW_KEY")
    assert value == "hello"


def test_set_key_overwrites_existing(vault_file):
    set_key(vault_file, PASSWORD, "staging", "FOO", "updated")
    assert get_key(vault_file, PASSWORD, "staging", "FOO") == "updated"


def test_set_key_creates_profile_if_missing(vault_file):
    set_key(vault_file, PASSWORD, "production", "DB_URL", "postgres://...")
    assert get_key(vault_file, PASSWORD, "production", "DB_URL") == "postgres://..."


def test_unset_key_removes_entry(vault_file):
    result = unset_key(vault_file, PASSWORD, "staging", "FOO")
    assert result is True
    with pytest.raises(EnvSetError):
        get_key(vault_file, PASSWORD, "staging", "FOO")


def test_unset_key_missing_key_returns_false(vault_file):
    result = unset_key(vault_file, PASSWORD, "staging", "DOES_NOT_EXIST")
    assert result is False


def test_unset_key_missing_profile_returns_false(vault_file):
    result = unset_key(vault_file, PASSWORD, "ghost", "FOO")
    assert result is False


def test_get_key_missing_profile_raises(vault_file):
    with pytest.raises(EnvSetError, match="Profile 'ghost' not found"):
        get_key(vault_file, PASSWORD, "ghost", "FOO")


def test_get_key_missing_key_raises(vault_file):
    with pytest.raises(EnvSetError, match="Key 'MISSING'"):
        get_key(vault_file, PASSWORD, "staging", "MISSING")


def test_list_keys_returns_all(vault_file):
    set_key(vault_file, PASSWORD, "staging", "BAR", "baz")
    pairs = list_keys(vault_file, PASSWORD, "staging")
    assert pairs["FOO"] == "bar"
    assert pairs["BAR"] == "baz"


def test_list_keys_missing_profile_raises(vault_file):
    with pytest.raises(EnvSetError):
        list_keys(vault_file, PASSWORD, "nonexistent")
