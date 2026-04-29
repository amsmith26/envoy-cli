"""Tests for envoy_cli.commands.usage_cmd."""

import pytest
from click.testing import CliRunner

from envoy_cli.vault import save_vault
from envoy_cli.commands.usage_cmd import usage


@pytest.fixture
def workspace(tmp_path):
    path = tmp_path / "test.vault"
    password = "secret"
    data = {"dev": {"API_KEY": "abc", "DB_URL": "postgres://localhost"}}
    save_vault(str(path), password, data)
    return str(path), password


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, args):
    path, pw = workspace
    return runner.invoke(usage, ["--vault-file", path, "--password", pw] + args)


def test_record_and_show(runner, workspace):
    result = invoke(runner, workspace, ["record", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "total: 1" in result.output

    result = invoke(runner, workspace, ["show", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "Access count: 1" in result.output
    assert "First access:" in result.output


def test_show_no_usage(runner, workspace):
    result = invoke(runner, workspace, ["show", "dev", "DB_URL"])
    assert result.exit_code == 0
    assert "No usage recorded" in result.output


def test_profile_usage_after_records(runner, workspace):
    invoke(runner, workspace, ["record", "dev", "API_KEY"])
    invoke(runner, workspace, ["record", "dev", "DB_URL"])
    result = invoke(runner, workspace, ["profile", "dev"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" in result.output


def test_profile_usage_empty(runner, workspace):
    result = invoke(runner, workspace, ["profile", "dev"])
    assert result.exit_code == 0
    assert "No usage data" in result.output


def test_top_keys_command(runner, workspace):
    invoke(runner, workspace, ["record", "dev", "API_KEY"])
    invoke(runner, workspace, ["record", "dev", "API_KEY"])
    invoke(runner, workspace, ["record", "dev", "DB_URL"])
    result = invoke(runner, workspace, ["top", "dev", "--n", "1"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "2 access" in result.output


def test_reset_command(runner, workspace):
    invoke(runner, workspace, ["record", "dev", "API_KEY"])
    result = invoke(runner, workspace, ["reset", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "cleared" in result.output

    result = invoke(runner, workspace, ["show", "dev", "API_KEY"])
    assert "No usage recorded" in result.output


def test_record_unknown_profile_exits_nonzero(runner, workspace):
    result = invoke(runner, workspace, ["record", "staging", "API_KEY"])
    assert result.exit_code != 0
    assert "Error" in result.output
