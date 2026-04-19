"""Integration tests for diff CLI commands."""

import os
import pytest
from click.testing import CliRunner
from envoy_cli.commands.diff_cmd import diff
from envoy_cli.vault import save_vault


PASSWORD = "testpass"


@pytest.fixture
def workspace(tmp_path):
    vault_file = str(tmp_path / ".env.vault")
    profiles = {
        "production": {"DB_HOST": "prod-db", "DEBUG": "false", "SHARED": "same"},
        "staging": {"DB_HOST": "stage-db", "NEW_KEY": "hello", "SHARED": "same"},
    }
    save_vault(vault_file, profiles, PASSWORD)

    env_file = str(tmp_path / ".env")
    with open(env_file, "w") as f:
        f.write('DB_HOST=local-db\nDEBUG=true\n')

    return {"vault": vault_file, "env": env_file, "dir": tmp_path}


@pytest.fixture
def runner():
    return CliRunner()


def test_diff_profiles_shows_changes(runner, workspace):
    result = runner.invoke(diff, [
        "profiles", "production", "staging",
        "--vault", workspace["vault"],
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_diff_profiles_no_differences(runner, workspace):
    result = runner.invoke(diff, [
        "profiles", "production", "production",
        "--vault", workspace["vault"],
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_profiles_missing_profile(runner, workspace):
    result = runner.invoke(diff, [
        "profiles", "production", "nonexistent",
        "--vault", workspace["vault"],
        "--password", PASSWORD,
    ])
    assert result.exit_code != 0


def test_diff_file_vs_profile(runner, workspace):
    result = runner.invoke(diff, [
        "file", "production",
        "--env-file", workspace["env"],
        "--vault", workspace["vault"],
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_diff_no_vault(runner, workspace):
    result = runner.invoke(diff, [
        "profiles", "production", "staging",
        "--vault", "/nonexistent/.env.vault",
        "--password", PASSWORD,
    ])
    assert result.exit_code != 0
