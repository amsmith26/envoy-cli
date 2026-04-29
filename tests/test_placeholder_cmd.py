"""Integration tests for placeholder CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.commands.placeholder_cmd import placeholder
from envoy_cli.vault import save_vault


@pytest.fixture()
def workspace(tmp_path):
    vault_path = str(tmp_path / "env.vault")
    data = {"profiles": {"dev": {"API_KEY": "", "SECRET": "abc123"}}}
    save_vault(vault_path, "pass", data)
    return vault_path


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(placeholder, ["--vault", workspace, "--password", "pass", *args])


def test_mark_and_list(runner, workspace):
    result = invoke(runner, workspace, "mark", "dev", "API_KEY", "--description", "Your API key")
    assert result.exit_code == 0
    assert "API_KEY" in result.output

    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "Your API key" in result.output


def test_list_no_placeholders(runner, workspace):
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "No placeholders" in result.output


def test_unmark_command(runner, workspace):
    invoke(runner, workspace, "mark", "dev", "API_KEY")
    result = invoke(runner, workspace, "unmark", "dev", "API_KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output
    assert "No placeholders remaining" in result.output


def test_check_unset_placeholder_exits_nonzero(runner, workspace):
    invoke(runner, workspace, "mark", "dev", "API_KEY")
    result = invoke(runner, workspace, "check", "dev")
    assert result.exit_code != 0
    assert "API_KEY" in result.output


def test_check_all_set_exits_zero(runner, workspace):
    invoke(runner, workspace, "mark", "dev", "SECRET")
    result = invoke(runner, workspace, "check", "dev")
    assert result.exit_code == 0
    assert "have values set" in result.output


def test_mark_unknown_profile_shows_error(runner, workspace):
    result = invoke(runner, workspace, "mark", "prod", "API_KEY")
    assert result.exit_code != 0
    assert "Error" in result.output
