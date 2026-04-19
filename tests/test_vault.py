"""Tests for envoy_cli.vault read/write operations."""

import json
from pathlib import Path
import pytest

from envoy_cli.vault import save_vault, load_vault, vault_exists, _vault_path

PASSWORD = "vault-pass-123"
SAMPLE_ENV = {"HOST": "db.local", "PORT": "5432", "TOKEN": "tok_abc"}


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("placeholder")
    return str(p)


def test_vault_path_extension(env_file):
    vp = _vault_path(env_file)
    assert vp.suffix == ".vault"


def test_save_and_load_vault(env_file):
    save_vault(SAMPLE_ENV, PASSWORD, env_file, backup=False)
    assert vault_exists(env_file)
    recovered = load_vault(env_file, PASSWORD)
    assert recovered == SAMPLE_ENV


def test_vault_file_is_json_encrypted(env_file):
    save_vault(SAMPLE_ENV, PASSWORD, env_file, backup=False)
    vault_file = _vault_path(env_file)
    data = json.loads(vault_file.read_text())
    # Values should not be plaintext
    for k, v in data.items():
        assert v != SAMPLE_ENV[k]


def test_load_vault_wrong_password(env_file):
    save_vault(SAMPLE_ENV, PASSWORD, env_file, backup=False)
    with pytest.raises(Exception):
        load_vault(env_file, "wrongpass")


def test_vault_not_exists(env_file):
    assert not vault_exists(env_file)


def test_load_vault_missing_file(env_file):
    with pytest.raises(FileNotFoundError):
        load_vault(env_file, PASSWORD)


def test_save_vault_creates_backup(env_file):
    save_vault(SAMPLE_ENV, PASSWORD, env_file, backup=False)
    # Second save with backup=True should create a .bak file
    save_vault(SAMPLE_ENV, PASSWORD, env_file, backup=True)
    vault_file = _vault_path(env_file)
    bak = Path(str(vault_file) + ".bak")
    assert bak.exists()
