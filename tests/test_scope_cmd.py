"""CLI tests for scope commands."""

import pytest
from click.testing import CliRunner

from envoy_cli.commands.scope_cmd import scope
from envoy_cli.vault import save_vault


PASSWORD = "cli-pass"


@pytest.fixture
def workspace(tmp_path):
    vault_path = str(tmp_path / "env.vault")
    data = {
        "dev": {"API_KEY": "abc123", "DB_PASS": "secret"},
        "prod": {"API_KEY": "xyz789", "DB_PASS": "prod-secret"},
    }
    save_vault(vault_path, PASSWORD, data)
    return vault_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(scope, ["--vault", workspace, "--password", PASSWORD, *args])


def test_set_scope_command(runner, workspace):
    result = invoke(runner, workspace, "set", "dev", "API_KEY", "--allow", "prod")
    assert result.exit_code == 0
    assert "prod" in result.output


def test_set_scope_unknown_profile(runner, workspace):
    result = invoke(runner, workspace, "set", "ghost", "API_KEY", "--allow", "prod")
    assert result.exit_code == 1
    assert "Error" in result.output


def test_list_scopes_empty(runner, workspace):
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "No scope restrictions" in result.output


def test_list_scopes_after_set(runner, workspace):
    invoke(runner, workspace, "set", "dev", "API_KEY", "--allow", "prod")
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "prod" in result.output


def test_remove_scope_command(runner, workspace):
    invoke(runner, workspace, "set", "dev", "DB_PASS", "--allow", "prod")
    result = invoke(runner, workspace, "remove", "dev", "DB_PASS")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_scope_not_found(runner, workspace):
    result = invoke(runner, workspace, "remove", "dev", "API_KEY")
    assert result.exit_code == 0
    assert "No scope restriction found" in result.output


def test_check_scope_allowed(runner, workspace):
    invoke(runner, workspace, "set", "dev", "API_KEY", "--allow", "prod")
    result = invoke(runner, workspace, "check", "dev", "API_KEY", "prod")
    assert result.exit_code == 0
    assert "allowed" in result.output


def test_check_scope_denied(runner, workspace):
    invoke(runner, workspace, "set", "dev", "API_KEY", "--allow", "prod")
    result = invoke(runner, workspace, "check", "dev", "API_KEY", "staging")
    assert result.exit_code == 0
    assert "denied" in result.output
