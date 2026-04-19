"""Integration tests for sync CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy_cli.commands.sync_cmd import sync


PASSWORD = "cli-test-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def workspace(tmp_path):
    env = tmp_path / ".env"
    env.write_text("SERVICE=api\nPORT=8080\n")
    vault = tmp_path / ".env.vault"
    return {"env": str(env), "vault": str(vault), "dir": tmp_path}


def test_push_and_list(runner, workspace):
    result = runner.invoke(sync, [
        "push", "--env", workspace["env"],
        "--vault", workspace["vault"],
        "--profile", "prod",
        "--password", PASSWORD,
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "prod" in result.output

    result = runner.invoke(sync, [
        "list", "--vault", workspace["vault"],
        "--password", PASSWORD,
    ])
    assert "prod" in result.output


def test_pull_command(runner, workspace):
    runner.invoke(sync, [
        "push", "--env", workspace["env"],
        "--vault", workspace["vault"],
        "--profile", "staging",
        "--password", PASSWORD,
        "--password", PASSWORD,
    ])
    out_env = str(Path(workspace["dir"]) / ".env.out")
    result = runner.invoke(sync, [
        "pull", "--env", out_env,
        "--vault", workspace["vault"],
        "--profile", "staging",
        "--no-backup",
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_delete_command(runner, workspace):
    runner.invoke(sync, [
        "push", "--env", workspace["env"],
        "--vault", workspace["vault"],
        "--profile", "temp",
        "--password", PASSWORD,
        "--password", PASSWORD,
    ])
    result = runner.invoke(sync, [
        "delete", "--vault", workspace["vault"],
        "--profile", "temp",
        "--password", PASSWORD,
    ])
    assert result.exit_code == 0
    assert "temp" in result.output


def test_pull_missing_profile_exits(runner, workspace):
    runner.invoke(sync, [
        "push", "--env", workspace["env"],
        "--vault", workspace["vault"],
        "--profile", "exists",
        "--password", PASSWORD,
        "--password", PASSWORD,
    ])
    result = runner.invoke(sync, [
        "pull", "--env", workspace["env"],
        "--vault", workspace["vault"],
        "--profile", "missing",
        "--password", PASSWORD,
    ])
    assert result.exit_code != 0
