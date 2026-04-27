"""Tests for envoy_cli.env_trim."""

from __future__ import annotations

import pytest

from envoy_cli.vault import save_vault, load_vault
from envoy_cli.env_trim import TrimError, trim_profile, preview_trim


PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.env.vault"
    vault = {
        "production": {
            "API_KEY": "  abc123  ",
            "DB_HOST": "localhost",
            "SECRET": " hidden ",
        },
        "staging": {
            "API_KEY": "stg-key",
        },
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_trim_profile_returns_changed_keys(vault_file):
    changed = trim_profile(vault_file, PASSWORD, "production")
    assert "API_KEY" in changed
    assert "SECRET" in changed


def test_trim_profile_unchanged_key_not_returned(vault_file):
    changed = trim_profile(vault_file, PASSWORD, "production")
    assert "DB_HOST" not in changed


def test_trim_profile_values_are_stripped(vault_file):
    changed = trim_profile(vault_file, PASSWORD, "production")
    assert changed["API_KEY"] == "abc123"
    assert changed["SECRET"] == "hidden"


def test_trim_profile_persisted(vault_file):
    trim_profile(vault_file, PASSWORD, "production")
    vault = load_vault(vault_file, PASSWORD)
    assert vault["production"]["API_KEY"] == "abc123"
    assert vault["production"]["SECRET"] == "hidden"


def test_trim_profile_with_key_filter(vault_file):
    changed = trim_profile(vault_file, PASSWORD, "production", keys=["API_KEY"])
    assert "API_KEY" in changed
    assert "SECRET" not in changed


def test_trim_profile_key_filter_persists_only_selected(vault_file):
    trim_profile(vault_file, PASSWORD, "production", keys=["API_KEY"])
    vault = load_vault(vault_file, PASSWORD)
    # SECRET should still have surrounding spaces
    assert vault["production"]["SECRET"] == " hidden "


def test_trim_profile_unknown_profile_raises(vault_file):
    with pytest.raises(TrimError, match="not found"):
        trim_profile(vault_file, PASSWORD, "nonexistent")


def test_trim_profile_no_changes_returns_empty(vault_file):
    # staging profile has no padded values
    changed = trim_profile(vault_file, PASSWORD, "staging")
    assert changed == {}


def test_preview_trim_does_not_mutate(vault_file):
    preview = preview_trim(vault_file, PASSWORD, "production")
    assert "API_KEY" in preview
    vault = load_vault(vault_file, PASSWORD)
    # Original padded value must still be there
    assert vault["production"]["API_KEY"] == "  abc123  "


def test_preview_trim_returns_correct_values(vault_file):
    preview = preview_trim(vault_file, PASSWORD, "production")
    assert preview["API_KEY"] == "abc123"
    assert preview["SECRET"] == "hidden"
