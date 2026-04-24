"""Tests for envoy_cli.env_flag."""

from __future__ import annotations

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_flag import (
    FlagError,
    get_flags,
    list_flagged_keys,
    remove_flag,
    set_flag,
)

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "production": {"DEBUG": "false", "CACHE": "true", "LOG_LEVEL": "info"},
        "staging": {"DEBUG": "true"},
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_get_flags_empty(vault_file):
    flags = get_flags(vault_file, PASSWORD, "production")
    assert flags == {}


def test_set_flag_returns_true(vault_file):
    result = set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    assert result is True


def test_set_flag_returns_false(vault_file):
    result = set_flag(vault_file, PASSWORD, "production", "CACHE", False)
    assert result is False


def test_set_flag_persisted(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    flags = get_flags(vault_file, PASSWORD, "production")
    assert flags["DEBUG"] is True


def test_set_flag_unknown_profile_raises(vault_file):
    with pytest.raises(FlagError, match="Profile 'ghost' not found"):
        set_flag(vault_file, PASSWORD, "ghost", "DEBUG", True)


def test_set_flag_unknown_key_raises(vault_file):
    with pytest.raises(FlagError, match="Key 'MISSING'"):
        set_flag(vault_file, PASSWORD, "production", "MISSING", True)


def test_remove_flag_returns_true_when_present(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    assert remove_flag(vault_file, PASSWORD, "production", "DEBUG") is True


def test_remove_flag_returns_false_when_absent(vault_file):
    assert remove_flag(vault_file, PASSWORD, "production", "DEBUG") is False


def test_remove_flag_clears_entry(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    remove_flag(vault_file, PASSWORD, "production", "DEBUG")
    flags = get_flags(vault_file, PASSWORD, "production")
    assert "DEBUG" not in flags


def test_list_flagged_keys_all(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    set_flag(vault_file, PASSWORD, "production", "CACHE", False)
    keys = list_flagged_keys(vault_file, PASSWORD, "production")
    assert keys == ["CACHE", "DEBUG"]


def test_list_flagged_keys_filter_on(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    set_flag(vault_file, PASSWORD, "production", "CACHE", False)
    keys = list_flagged_keys(vault_file, PASSWORD, "production", value=True)
    assert keys == ["DEBUG"]


def test_list_flagged_keys_filter_off(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    set_flag(vault_file, PASSWORD, "production", "CACHE", False)
    keys = list_flagged_keys(vault_file, PASSWORD, "production", value=False)
    assert keys == ["CACHE"]


def test_flags_isolated_between_profiles(vault_file):
    set_flag(vault_file, PASSWORD, "production", "DEBUG", True)
    staging_flags = get_flags(vault_file, PASSWORD, "staging")
    assert "DEBUG" not in staging_flags
