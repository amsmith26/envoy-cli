"""Tests for envoy_cli.merge."""

import json
import pytest
from pathlib import Path
from envoy_cli.vault import save_vault, load_vault
from envoy_cli.merge import merge_profiles, list_merge_candidates, MergeError

PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging.db", "API_KEY": "abc123"},
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_merge_adds_missing_keys(vault_file):
    result = merge_profiles(vault_file, PASSWORD, ["dev"], "staging")
    assert "DB_PORT" in result["added"]
    assert "DEBUG" in result["added"]


def test_merge_does_not_overwrite_by_default(vault_file):
    result = merge_profiles(vault_file, PASSWORD, ["dev"], "staging")
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["DB_HOST"] == "staging.db"
    assert "DB_HOST" not in result["added"]
    assert "DB_HOST" not in result["updated"]


def test_merge_overwrites_when_flag_set(vault_file):
    result = merge_profiles(vault_file, PASSWORD, ["dev"], "staging", overwrite=True)
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["DB_HOST"] == "localhost"
    assert "DB_HOST" in result["updated"]


def test_merge_creates_target_if_missing(vault_file):
    result = merge_profiles(vault_file, PASSWORD, ["dev"], "production")
    vault = load_vault(vault_file, PASSWORD)
    assert "production" in vault
    assert vault["production"]["DB_HOST"] == "localhost"
    assert set(result["added"]) == {"DB_HOST", "DB_PORT", "DEBUG"}


def test_merge_with_key_filter(vault_file):
    result = merge_profiles(vault_file, PASSWORD, ["dev"], "staging", keys=["DB_PORT"])
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["DB_PORT"] == "5432"
    assert "DEBUG" not in vault["staging"]
    assert result["added"] == ["DB_PORT"]


def test_merge_unknown_source_raises(vault_file):
    with pytest.raises(MergeError, match="not found"):
        merge_profiles(vault_file, PASSWORD, ["nonexistent"], "staging")


def test_merge_multiple_sources(vault_file):
    vault = load_vault(vault_file, PASSWORD)
    vault["extra"] = {"EXTRA_KEY": "extra_val"}
    save_vault(vault_file, PASSWORD, vault)

    result = merge_profiles(vault_file, PASSWORD, ["dev", "extra"], "staging")
    assert "EXTRA_KEY" in result["added"]
    assert "DB_PORT" in result["added"]


def test_list_merge_candidates(vault_file):
    result = list_merge_candidates(vault_file, PASSWORD, "dev", "staging")
    assert "DB_PORT" in result["would_add"]
    assert "DEBUG" in result["would_add"]
    assert "DB_HOST" in result["would_update"]


def test_list_merge_candidates_no_target(vault_file):
    result = list_merge_candidates(vault_file, PASSWORD, "dev", "new_profile")
    assert set(result["would_add"]) == {"DB_HOST", "DB_PORT", "DEBUG"}
    assert result["would_update"] == []


def test_list_merge_candidates_unknown_source_raises(vault_file):
    with pytest.raises(MergeError):
        list_merge_candidates(vault_file, PASSWORD, "ghost", "staging")
