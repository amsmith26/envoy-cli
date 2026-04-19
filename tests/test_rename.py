import pytest
import json
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.rename import rename_key, rename_key_all_profiles, RenameError

PASSWORD = "test-pass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    data = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432"},
        "prod": {"DB_HOST": "prod.db", "API_KEY": "secret"},
    }
    save_vault(str(path), PASSWORD, data)
    return str(path)


def test_rename_key_success(vault_file):
    result = rename_key(vault_file, PASSWORD, "dev", "DB_HOST", "DATABASE_HOST")
    assert result is True


def test_rename_key_value_preserved(vault_file):
    rename_key(vault_file, PASSWORD, "dev", "DB_HOST", "DATABASE_HOST")
    from envoy_cli.vault import load_vault
    data = load_vault(vault_file, PASSWORD)
    assert data["dev"]["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in data["dev"]


def test_rename_key_not_found_returns_false(vault_file):
    result = rename_key(vault_file, PASSWORD, "dev", "NONEXISTENT", "NEW_KEY")
    assert result is False


def test_rename_key_conflict_raises(vault_file):
    with pytest.raises(RenameError, match="already exists"):
        rename_key(vault_file, PASSWORD, "dev", "DB_HOST", "DB_PORT")


def test_rename_key_missing_profile_raises(vault_file):
    with pytest.raises(RenameError, match="does not exist"):
        rename_key(vault_file, PASSWORD, "staging", "DB_HOST", "DATABASE_HOST")


def test_rename_key_missing_vault_raises(tmp_path):
    with pytest.raises(RenameError, match="Vault not found"):
        rename_key(str(tmp_path / "missing.vault"), PASSWORD, "dev", "A", "B")


def test_rename_key_all_profiles(vault_file):
    results = rename_key_all_profiles(vault_file, PASSWORD, "DB_HOST", "DATABASE_HOST")
    assert results["dev"] is True
    assert results["prod"] is True


def test_rename_key_all_profiles_partial(vault_file):
    results = rename_key_all_profiles(vault_file, PASSWORD, "API_KEY", "API_SECRET")
    assert results["prod"] is True
    assert results["dev"] is False


def test_rename_key_all_profiles_conflict_raises(vault_file):
    with pytest.raises(RenameError, match="already exists"):
        rename_key_all_profiles(vault_file, PASSWORD, "DB_HOST", "DB_PORT")
