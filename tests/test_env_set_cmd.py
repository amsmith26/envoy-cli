"""Integration tests for the env_set CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.commands.env_set_cmd import env_set

PASSWORD = "cli-test-pass"


@pytest.fixture
def workspace(tmp_path):
    vault = tmp_path / "proj.env.vault"
    save_vault(str(vault), PASSWORD, {"dev": {"API_KEY": "abc123"}})
    return {"vault": str(vault), "tmp": tmp_path}


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(
        env_set,
        ["--vault", workspace["vault"], "--password", PASSWORD, *args],
    )


def test_set_and_get_key(runner, workspace):
    result = invoke(runner, workspace, "set", "dev", "SECRET", "mysecret")
    assert result.exit_code == 0
    assert "Set SECRET" in result.output

    result = invoke(runner, workspace, "get", "dev", "SECRET")
    assert result.exit_code == 0
    assert "mysecret" in result.output


def test_unset_existing_key(runner, workspace):
    result = invoke(runner, workspace, "unset", "dev", "API_KEY")
    assert result.exit_code == 0
    assert "Unset 'API_KEY'" in result.output


def test_unset_missing_key(runner, workspace):
    result = invoke(runner, workspace, "unset", "dev", "GHOST")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_get_missing_key_exits_nonzero(runner, workspace):
    result = invoke(runner, workspace, "get", "dev", "NOPE")
    assert result.exit_code != 0


def test_list_keys_shows_entries(runner, workspace):
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "API_KEY=abc123" in result.output


def test_list_keys_missing_profile_exits_nonzero(runner, workspace):
    result = invoke(runner, workspace, "list", "ghost")
    assert result.exit_code != 0


def test_set_creates_new_profile(runner, workspace):
    result = invoke(runner, workspace, "set", "production", "DB", "pg://")
    assert result.exit_code == 0
    result = invoke(runner, workspace, "get", "production", "DB")
    assert "pg://" in result.output
