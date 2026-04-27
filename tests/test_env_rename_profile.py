"""Tests for envoy_cli.env_rename_profile."""

import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.env_rename_profile import (
    rename_profile,
    list_profile_names,
    RenameProfileError,
)

PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod": {"DB_HOST": "prod.db.internal", "DEBUG": "false"},
    }
    save_vault(path, PASSWORD, data)
    return path


def test_rename_profile_success(vault_file):
    result = rename_profile(vault_file, PASSWORD, "dev", "development")
    assert result == "development"


def test_rename_profile_new_name_in_vault(vault_file):
    rename_profile(vault_file, PASSWORD, "dev", "development")
    names = list_profile_names(vault_file, PASSWORD)
    assert "development" in names
    assert "dev" not in names


def test_rename_profile_values_preserved(vault_file):
    from envoy_cli.vault import load_vault
    rename_profile(vault_file, PASSWORD, "dev", "staging")
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["DB_HOST"] == "localhost"
    assert vault["staging"]["DEBUG"] == "true"


def test_rename_profile_old_not_found_raises(vault_file):
    with pytest.raises(RenameProfileError, match="does not exist"):
        rename_profile(vault_file, PASSWORD, "nonexistent", "new_name")


def test_rename_profile_new_already_exists_raises(vault_file):
    with pytest.raises(RenameProfileError, match="already exists"):
        rename_profile(vault_file, PASSWORD, "dev", "prod")


def test_rename_profile_empty_new_name_raises(vault_file):
    with pytest.raises(RenameProfileError, match="must not be empty"):
        rename_profile(vault_file, PASSWORD, "dev", "   ")


def test_list_profile_names_sorted(vault_file):
    names = list_profile_names(vault_file, PASSWORD)
    assert names == ["dev", "prod"]


def test_list_profile_names_after_rename(vault_file):
    rename_profile(vault_file, PASSWORD, "dev", "alpha")
    names = list_profile_names(vault_file, PASSWORD)
    assert names == ["alpha", "prod"]


def test_rename_does_not_affect_other_profiles(vault_file):
    from envoy_cli.vault import load_vault
    rename_profile(vault_file, PASSWORD, "dev", "staging")
    vault = load_vault(vault_file, PASSWORD)
    assert vault["prod"]["DB_HOST"] == "prod.db.internal"
