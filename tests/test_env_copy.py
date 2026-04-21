"""Tests for envoy_cli.env_copy."""

import json
import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.env_copy import copy_key, copy_keys, EnvCopyError

PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    data = {
        "production": {"DB_HOST": "prod-db", "API_KEY": "prod-key"},
        "staging": {"DB_HOST": "staging-db"},
    }
    save_vault(str(path), PASSWORD, data)
    return str(path)


def test_copy_key_success(vault_file):
    value = copy_key(vault_file, PASSWORD, "production", "staging", "API_KEY")
    assert value == "prod-key"


def test_copy_key_persisted(vault_file):
    from envoy_cli.vault import load_vault

    copy_key(vault_file, PASSWORD, "production", "staging", "API_KEY")
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["API_KEY"] == "prod-key"


def test_copy_key_creates_dst_profile(vault_file):
    from envoy_cli.vault import load_vault

    copy_key(vault_file, PASSWORD, "production", "newenv", "DB_HOST")
    vault = load_vault(vault_file, PASSWORD)
    assert "newenv" in vault
    assert vault["newenv"]["DB_HOST"] == "prod-db"


def test_copy_key_missing_src_profile(vault_file):
    with pytest.raises(EnvCopyError, match="Source profile 'ghost' not found"):
        copy_key(vault_file, PASSWORD, "ghost", "staging", "DB_HOST")


def test_copy_key_missing_key(vault_file):
    with pytest.raises(EnvCopyError, match="Key 'MISSING' not found"):
        copy_key(vault_file, PASSWORD, "production", "staging", "MISSING")


def test_copy_key_no_overwrite_raises(vault_file):
    with pytest.raises(EnvCopyError, match="already exists"):
        copy_key(vault_file, PASSWORD, "production", "staging", "DB_HOST")


def test_copy_key_overwrite_succeeds(vault_file):
    from envoy_cli.vault import load_vault

    copy_key(vault_file, PASSWORD, "production", "staging", "DB_HOST", overwrite=True)
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["DB_HOST"] == "prod-db"


def test_copy_keys_multiple(vault_file):
    from envoy_cli.vault import load_vault

    result = copy_keys(
        vault_file, PASSWORD, "production", "staging", ["API_KEY"], overwrite=False
    )
    assert result == {"API_KEY": "prod-key"}
    vault = load_vault(vault_file, PASSWORD)
    assert vault["staging"]["API_KEY"] == "prod-key"


def test_copy_keys_partial_missing_raises(vault_file):
    with pytest.raises(EnvCopyError, match="Key 'NOPE' not found"):
        copy_keys(vault_file, PASSWORD, "production", "staging", ["API_KEY", "NOPE"])


def test_copy_keys_returns_copied_dict(vault_file):
    result = copy_keys(
        vault_file, PASSWORD, "production", "staging", ["API_KEY"], overwrite=False
    )
    assert isinstance(result, dict)
    assert "API_KEY" in result
