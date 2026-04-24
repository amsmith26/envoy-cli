"""Integration tests for the archive CLI commands."""

import pytest
from click.testing import CliRunner

from envoy_cli.commands.archive_cmd import archive
from envoy_cli.vault import save_vault

PASSWORD = "cli-test-pass"


@pytest.fixture()
def workspace(tmp_path):
    vault_path = str(tmp_path / "env.vault")
    vault = {
        "dev": {"APP_ENV": "development", "PORT": "8000"},
        "staging": {"APP_ENV": "staging", "PORT": "9000"},
    }
    save_vault(vault_path, PASSWORD, vault)
    return vault_path


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(
        archive,
        ["--vault", workspace, "--password", PASSWORD, *args],
    )


def test_list_archived_empty(runner, workspace):
    result = invoke(runner, workspace, "list")
    assert result.exit_code == 0
    assert "No archived profiles" in result.output


def test_archive_and_list(runner, workspace):
    invoke(runner, workspace, "add", "dev")
    result = invoke(runner, workspace, "list")
    assert result.exit_code == 0
    assert "dev" in result.output


def test_archive_nonexistent_profile(runner, workspace):
    result = invoke(runner, workspace, "add", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_restore_command(runner, workspace):
    invoke(runner, workspace, "add", "dev")
    result = invoke(runner, workspace, "restore", "dev")
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_restore_missing_raises(runner, workspace):
    result = invoke(runner, workspace, "restore", "dev")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_archived_profile(runner, workspace):
    invoke(runner, workspace, "add", "dev")
    result = invoke(runner, workspace, "show", "dev")
    assert result.exit_code == 0
    assert "APP_ENV=development" in result.output
    assert "PORT=8000" in result.output


def test_show_non_archived_raises(runner, workspace):
    result = invoke(runner, workspace, "show", "dev")
    assert result.exit_code != 0
    assert "not found" in result.output
