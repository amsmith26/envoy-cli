import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.commands.snapshot_cmd import snapshot
from envoy_cli.vault import save_vault

PASSWORD = "testpass"


@pytest.fixture
def workspace(tmp_path):
    vault = tmp_path / ".env.vault"
    data = {"production": {"API_KEY": "abc", "DEBUG": "false"}}
    save_vault(str(vault), PASSWORD, data)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_create_snapshot(workspace, runner):
    vault = str(workspace / ".env.vault")
    result = runner.invoke(
        snapshot,
        ["create", "production", "--vault", vault, "--password", PASSWORD, "--label", "v1"],
    )
    assert result.exit_code == 0
    assert "v1" in result.output


def test_list_snapshots(workspace, runner):
    vault = str(workspace / ".env.vault")
    runner.invoke(
        snapshot,
        ["create", "production", "--vault", vault, "--password", PASSWORD, "--label", "snap1"],
    )
    result = runner.invoke(
        snapshot,
        ["list", "production", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_list_snapshots_empty(workspace, runner):
    vault = str(workspace / ".env.vault")
    result = runner.invoke(
        snapshot,
        ["list", "production", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_restore_snapshot(workspace, runner):
    vault = str(workspace / ".env.vault")
    runner.invoke(
        snapshot,
        ["create", "production", "--vault", vault, "--password", PASSWORD, "--label", "before"],
    )
    result = runner.invoke(
        snapshot,
        ["restore", "production", "before", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "restored" in result.output


def test_delete_snapshot(workspace, runner):
    vault = str(workspace / ".env.vault")
    runner.invoke(
        snapshot,
        ["create", "production", "--vault", vault, "--password", PASSWORD, "--label", "tmp"],
    )
    result = runner.invoke(
        snapshot,
        ["delete", "production", "tmp", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_create_snapshot_missing_profile(workspace, runner):
    vault = str(workspace / ".env.vault")
    result = runner.invoke(
        snapshot,
        ["create", "ghost", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
