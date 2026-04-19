"""Tests for vault password rotation."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envoy_cli.vault import save_vault, load_vault
from envoy_cli.rotate import rotate_vault_password
from envoy_cli.commands.rotate_cmd import rotate


@pytest.fixture()
def vault_file(tmp_path: Path) -> str:
    path = str(tmp_path / "test.vault")
    data = {
        "dev": {"DB_URL": "postgres://localhost/dev", "SECRET": "abc"},
        "prod": {"DB_URL": "postgres://localhost/prod", "SECRET": "xyz"},
    }
    save_vault(path, data, "old-pass")
    return path


def test_rotate_returns_profile_names(vault_file):
    profiles = rotate_vault_password(vault_file, "old-pass", "new-pass")
    assert set(profiles) == {"dev", "prod"}


def test_rotate_new_password_works(vault_file):
    rotate_vault_password(vault_file, "old-pass", "new-pass")
    data = load_vault(vault_file, "new-pass")
    assert data["dev"]["DB_URL"] == "postgres://localhost/dev"


def test_rotate_old_password_fails_after_rotation(vault_file):
    rotate_vault_password(vault_file, "old-pass", "new-pass")
    with pytest.raises(Exception):
        load_vault(vault_file, "old-pass")


def test_rotate_wrong_old_password_raises(vault_file):
    with pytest.raises(Exception):
        rotate_vault_password(vault_file, "wrong", "new-pass")


def test_rotate_missing_vault_raises(tmp_path):
    with pytest.raises(ValueError, match="Vault not found"):
        rotate_vault_password(str(tmp_path / "ghost.vault"), "a", "b")


def test_rotate_cmd_success(vault_file):
    runner = CliRunner()
    result = runner.invoke(
        rotate,
        ["run", vault_file, "--old-password", "old-pass", "--new-password", "new-pass"],
    )
    assert result.exit_code == 0
    assert "Rotated 2 profile(s)" in result.output


def test_rotate_cmd_wrong_password(vault_file):
    runner = CliRunner()
    result = runner.invoke(
        rotate,
        ["run", vault_file, "--old-password", "bad", "--new-password", "new-pass"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output
