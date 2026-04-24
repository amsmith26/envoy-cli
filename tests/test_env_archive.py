"""Tests for envoy_cli.env_archive."""

import pytest

from envoy_cli.env_archive import (
    ArchiveError,
    archive_profile,
    get_archived_env,
    list_archived,
    unarchive_profile,
)
from envoy_cli.vault import save_vault

PASSWORD = "test-password"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "dev": {"APP_ENV": "development", "DEBUG": "true"},
        "prod": {"APP_ENV": "production", "DEBUG": "false"},
    }
    save_vault(path, PASSWORD, vault)
    return path


def test_list_archived_empty(vault_file):
    assert list_archived(vault_file, PASSWORD) == []


def test_archive_profile_removes_from_active(vault_file):
    archive_profile(vault_file, PASSWORD, "dev")
    archived = list_archived(vault_file, PASSWORD)
    assert "dev" in archived


def test_archive_profile_returns_sorted_list(vault_file):
    result = archive_profile(vault_file, PASSWORD, "dev")
    assert result == sorted(result)


def test_archive_nonexistent_profile_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found"):
        archive_profile(vault_file, PASSWORD, "staging")


def test_archive_already_archived_raises(vault_file):
    archive_profile(vault_file, PASSWORD, "dev")
    with pytest.raises(ArchiveError, match="already archived"):
        archive_profile(vault_file, PASSWORD, "dev")


def test_unarchive_restores_profile(vault_file):
    archive_profile(vault_file, PASSWORD, "dev")
    unarchive_profile(vault_file, PASSWORD, "dev")
    assert "dev" not in list_archived(vault_file, PASSWORD)


def test_unarchive_nonexistent_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found"):
        unarchive_profile(vault_file, PASSWORD, "ghost")


def test_unarchive_conflict_raises(vault_file):
    """If active profile with same name exists, unarchive should raise."""
    from envoy_cli.vault import load_vault, save_vault as sv

    archive_profile(vault_file, PASSWORD, "dev")
    # Re-add 'dev' as an active profile manually
    vault = load_vault(vault_file, PASSWORD)
    vault["dev"] = {"APP_ENV": "conflict"}
    sv(vault_file, PASSWORD, vault)
    with pytest.raises(ArchiveError, match="already exists"):
        unarchive_profile(vault_file, PASSWORD, "dev")


def test_get_archived_env_returns_correct_values(vault_file):
    archive_profile(vault_file, PASSWORD, "dev")
    env = get_archived_env(vault_file, PASSWORD, "dev")
    assert env["APP_ENV"] == "development"
    assert env["DEBUG"] == "true"


def test_get_archived_env_missing_raises(vault_file):
    with pytest.raises(ArchiveError, match="not found"):
        get_archived_env(vault_file, PASSWORD, "dev")


def test_values_preserved_after_roundtrip(vault_file):
    archive_profile(vault_file, PASSWORD, "prod")
    unarchive_profile(vault_file, PASSWORD, "prod")
    from envoy_cli.vault import load_vault

    vault = load_vault(vault_file, PASSWORD)
    assert vault["prod"]["APP_ENV"] == "production"
