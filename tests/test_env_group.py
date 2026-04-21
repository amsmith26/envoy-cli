"""Tests for envoy_cli.env_group."""

import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.env_group import (
    add_key_to_group,
    remove_key_from_group,
    list_groups,
    get_keys_in_group,
    delete_group,
    GroupError,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "production": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"},
        "staging": {"DB_HOST": "staging-host"},
    }
    save_vault(path, PASSWORD, vault)
    return path


def test_add_key_to_group_success(vault_file):
    keys = add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    assert "DB_HOST" in keys


def test_add_key_sorted(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_PORT")
    keys = add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    assert keys == sorted(keys)


def test_add_duplicate_key_no_duplicates(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    keys = add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    assert keys.count("DB_HOST") == 1


def test_add_key_unknown_profile_raises(vault_file):
    with pytest.raises(GroupError, match="Profile"):
        add_key_to_group(vault_file, PASSWORD, "nonexistent", "grp", "DB_HOST")


def test_add_key_unknown_key_raises(vault_file):
    with pytest.raises(GroupError, match="Key"):
        add_key_to_group(vault_file, PASSWORD, "production", "grp", "MISSING_KEY")


def test_list_groups_empty(vault_file):
    groups = list_groups(vault_file, PASSWORD, "production")
    assert groups == {}


def test_list_groups_after_add(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_PORT")
    groups = list_groups(vault_file, PASSWORD, "production")
    assert "database" in groups
    assert set(groups["database"]) == {"DB_HOST", "DB_PORT"}


def test_get_keys_in_group(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "secrets", "SECRET")
    keys = get_keys_in_group(vault_file, PASSWORD, "production", "secrets")
    assert keys == ["SECRET"]


def test_get_keys_in_nonexistent_group(vault_file):
    keys = get_keys_in_group(vault_file, PASSWORD, "production", "ghost")
    assert keys == []


def test_remove_key_from_group(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_PORT")
    remaining = remove_key_from_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    assert "DB_HOST" not in remaining
    assert "DB_PORT" in remaining


def test_remove_last_key_deletes_group(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "solo", "SECRET")
    remove_key_from_group(vault_file, PASSWORD, "production", "solo", "SECRET")
    groups = list_groups(vault_file, PASSWORD, "production")
    assert "solo" not in groups


def test_remove_key_not_in_group_raises(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    with pytest.raises(GroupError, match="not in group"):
        remove_key_from_group(vault_file, PASSWORD, "production", "database", "SECRET")


def test_delete_group(vault_file):
    add_key_to_group(vault_file, PASSWORD, "production", "database", "DB_HOST")
    delete_group(vault_file, PASSWORD, "production", "database")
    groups = list_groups(vault_file, PASSWORD, "production")
    assert "database" not in groups


def test_delete_nonexistent_group_raises(vault_file):
    with pytest.raises(GroupError, match="not found"):
        delete_group(vault_file, PASSWORD, "production", "ghost")
