"""Tests for envoy_cli.env_required module."""

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_required import (
    RequiredError,
    get_required_keys,
    mark_required,
    unmark_required,
    check_required,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    password = "secret"
    vault = {
        "profiles": {
            "production": {
                "DATABASE_URL": "postgres://localhost/db",
                "SECRET_KEY": "abc123",
                "OPTIONAL_KEY": "",
            }
        }
    }
    save_vault(str(path), password, vault)
    return str(path), password


def test_get_required_keys_empty(vault_file):
    path, pw = vault_file
    assert get_required_keys(path, pw, "production") == []


def test_mark_required_returns_sorted_list(vault_file):
    path, pw = vault_file
    result = mark_required(path, pw, "production", "DATABASE_URL")
    assert result == ["DATABASE_URL"]


def test_mark_required_persisted(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "SECRET_KEY")
    assert "SECRET_KEY" in get_required_keys(path, pw, "production")


def test_mark_multiple_keys_sorted(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "SECRET_KEY")
    result = mark_required(path, pw, "production", "DATABASE_URL")
    assert result == ["DATABASE_URL", "SECRET_KEY"]


def test_mark_duplicate_no_duplicates(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "DATABASE_URL")
    result = mark_required(path, pw, "production", "DATABASE_URL")
    assert result.count("DATABASE_URL") == 1


def test_mark_required_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(RequiredError, match="Profile 'staging' does not exist"):
        mark_required(path, pw, "staging", "DATABASE_URL")


def test_mark_required_unknown_key_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(RequiredError, match="Key 'MISSING' not found"):
        mark_required(path, pw, "production", "MISSING")


def test_unmark_required_removes_key(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "DATABASE_URL")
    result = unmark_required(path, pw, "production", "DATABASE_URL")
    assert "DATABASE_URL" not in result


def test_unmark_required_not_marked_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(RequiredError, match="not marked as required"):
        unmark_required(path, pw, "production", "DATABASE_URL")


def test_check_required_all_present(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "DATABASE_URL")
    mark_required(path, pw, "production", "SECRET_KEY")
    missing = check_required(path, pw, "production")
    assert missing == []


def test_check_required_detects_empty_value(vault_file):
    path, pw = vault_file
    mark_required(path, pw, "production", "OPTIONAL_KEY")
    missing = check_required(path, pw, "production")
    assert "OPTIONAL_KEY" in missing


def test_check_required_no_required_keys(vault_file):
    path, pw = vault_file
    assert check_required(path, pw, "production") == []
