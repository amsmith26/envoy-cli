"""Tests for envoy_cli.env_mask."""

import pytest

from envoy_cli.vault import save_vault, load_vault
from envoy_cli.env_mask import (
    MaskError,
    get_masked_keys,
    mask_key,
    unmask_key,
    apply_masks,
)

PASSWORD = "s3cr3t"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "production": {"API_KEY": "abc123", "DB_PASS": "hunter2", "DEBUG": "false"},
        "staging": {"API_KEY": "xyz", "TOKEN": "tok"},
    }
    save_vault(path, PASSWORD, vault)
    return path


def test_mask_key_success(vault_file):
    result = mask_key(vault_file, PASSWORD, "production", "API_KEY")
    assert "API_KEY" in result


def test_mask_key_persisted(vault_file):
    mask_key(vault_file, PASSWORD, "production", "API_KEY")
    vault = load_vault(vault_file, PASSWORD)
    keys = get_masked_keys(vault, "production")
    assert "API_KEY" in keys


def test_mask_multiple_keys_sorted(vault_file):
    mask_key(vault_file, PASSWORD, "production", "DB_PASS")
    result = mask_key(vault_file, PASSWORD, "production", "API_KEY")
    assert result == ["API_KEY", "DB_PASS"]


def test_mask_duplicate_no_duplicates(vault_file):
    mask_key(vault_file, PASSWORD, "production", "API_KEY")
    result = mask_key(vault_file, PASSWORD, "production", "API_KEY")
    assert result.count("API_KEY") == 1


def test_mask_unknown_profile_raises(vault_file):
    with pytest.raises(MaskError, match="Profile"):
        mask_key(vault_file, PASSWORD, "nonexistent", "API_KEY")


def test_mask_unknown_key_raises(vault_file):
    with pytest.raises(MaskError, match="Key"):
        mask_key(vault_file, PASSWORD, "production", "MISSING_KEY")


def test_unmask_key_removes_entry(vault_file):
    mask_key(vault_file, PASSWORD, "production", "API_KEY")
    result = unmask_key(vault_file, PASSWORD, "production", "API_KEY")
    assert "API_KEY" not in result


def test_unmask_nonexistent_key_no_error(vault_file):
    result = unmask_key(vault_file, PASSWORD, "production", "NEVER_MASKED")
    assert isinstance(result, list)


def test_get_masked_keys_empty(vault_file):
    vault = load_vault(vault_file, PASSWORD)
    assert get_masked_keys(vault, "staging") == []


def test_apply_masks_replaces_values():
    env = {"API_KEY": "secret", "DEBUG": "true"}
    result = apply_masks(env, ["API_KEY"])
    assert result["API_KEY"] == "***"
    assert result["DEBUG"] == "true"


def test_apply_masks_custom_placeholder():
    env = {"TOKEN": "abc"}
    result = apply_masks(env, ["TOKEN"], placeholder="[REDACTED]")
    assert result["TOKEN"] == "[REDACTED]"


def test_apply_masks_empty_mask_list():
    env = {"A": "1", "B": "2"}
    result = apply_masks(env, [])
    assert result == env
