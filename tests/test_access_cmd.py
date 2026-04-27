"""CLI integration tests for the access commands."""

import pytest
from click.testing import CliRunner

from envoy_cli.commands.access_cmd import access
from envoy_cli.vault import save_vault


@pytest.fixture()
def workspace(tmp_path):
    vault_path = str(tmp_path / "test.vault")
    save_vault(vault_path, "secret", {"production": {"API_KEY": "abc"}, "staging": {"API_KEY": "xyz"}})
    return vault_path


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(access, ["--vault", workspace, "--password", "secret"] + list(args))


def test_grant_and_show(runner, workspace):
    result = invoke(runner, workspace, "grant", "production", "alice", "--role", "read")
    assert result.exit_code == 0
    assert "Granted 'read' to 'alice'" in result.output

    result = invoke(runner, workspace, "show", "production")
    assert result.exit_code == 0
    assert "alice" in result.output


def test_revoke_command(runner, workspace):
    invoke(runner, workspace, "grant", "production", "bob", "--role", "write")
    result = invoke(runner, workspace, "revoke", "production", "bob", "--role", "write")
    assert result.exit_code == 0
    assert "Revoked 'write' from 'bob'" in result.output


def test_check_allowed(runner, workspace):
    invoke(runner, workspace, "grant", "staging", "dev", "--role", "read")
    result = invoke(runner, workspace, "check", "staging", "dev", "--role", "read")
    assert result.exit_code == 0
    assert "ALLOWED" in result.output


def test_check_denied(runner, workspace):
    result = invoke(runner, workspace, "check", "staging", "nobody", "--role", "write")
    assert result.exit_code == 0
    assert "DENIED" in result.output


def test_grant_unknown_profile_error(runner, workspace):
    result = invoke(runner, workspace, "grant", "ghost", "alice", "--role", "read")
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_show_unknown_profile_error(runner, workspace):
    result = invoke(runner, workspace, "show", "nonexistent")
    assert result.exit_code != 0
