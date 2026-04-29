"""Integration tests for the freeze CLI commands."""
import pytest
from click.testing import CliRunner

from envoy_cli.commands.freeze_cmd import freeze
from envoy_cli.vault import save_vault


@pytest.fixture()
def workspace(tmp_path):
    vault_path = str(tmp_path / "env.vault")
    password = "pass123"
    vault = {
        "production": {"API_KEY": "prod-key"},
        "staging": {"API_KEY": "stg-key"},
    }
    save_vault(vault_path, password, vault)
    return vault_path, password


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    vault_path, password = workspace
    return runner.invoke(
        freeze,
        ["--vault", vault_path, "--password", password, *args],
    )


def test_freeze_and_list(runner, workspace):
    result = invoke(runner, workspace, "lock", "production")
    assert result.exit_code == 0
    assert "frozen" in result.output

    result = invoke(runner, workspace, "list")
    assert result.exit_code == 0
    assert "production" in result.output


def test_list_no_frozen(runner, workspace):
    result = invoke(runner, workspace, "list")
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_unfreeze_command(runner, workspace):
    invoke(runner, workspace, "lock", "staging")
    result = invoke(runner, workspace, "unlock", "staging")
    assert result.exit_code == 0
    assert "unfrozen" in result.output


def test_freeze_unknown_profile_error(runner, workspace):
    result = invoke(runner, workspace, "lock", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_unfreeze_not_frozen_error(runner, workspace):
    result = invoke(runner, workspace, "unlock", "production")
    assert result.exit_code != 0
    assert "not frozen" in result.output


def test_check_frozen_true(runner, workspace):
    invoke(runner, workspace, "lock", "production")
    result = invoke(runner, workspace, "check", "production")
    assert result.exit_code == 0
    assert "frozen" in result.output


def test_check_frozen_false(runner, workspace):
    result = invoke(runner, workspace, "check", "staging")
    assert result.exit_code == 0
    assert "not frozen" in result.output
