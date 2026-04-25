"""Tests for envoy_cli.commands.inherit_cmd."""

import pytest
from click.testing import CliRunner

from envoy_cli.commands.inherit_cmd import inherit
from envoy_cli.vault import save_vault


@pytest.fixture
def workspace(tmp_path):
    vault_path = str(tmp_path / "test.vault")
    vault = {
        "profiles": {
            "base": {"HOST": "localhost", "PORT": "5432"},
            "dev": {"DEBUG": "true"},
        }
    }
    save_vault(vault_path, "secret", vault)
    return vault_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, cmd, vault_path, args):
    return runner.invoke(cmd, ["--vault-file", vault_path, "--password", "secret"] + args)


def test_set_parent_command(runner, workspace):
    result = invoke(runner, inherit, workspace, ["set", "dev", "base"])
    assert result.exit_code == 0
    assert "inherits from 'base'" in result.output


def test_show_parent_after_set(runner, workspace):
    invoke(runner, inherit, workspace, ["set", "dev", "base"])
    result = invoke(runner, inherit, workspace, ["show", "dev"])
    assert result.exit_code == 0
    assert "base" in result.output


def test_show_no_parent(runner, workspace):
    result = invoke(runner, inherit, workspace, ["show", "dev"])
    assert result.exit_code == 0
    assert "no parent" in result.output


def test_remove_parent_command(runner, workspace):
    invoke(runner, inherit, workspace, ["set", "dev", "base"])
    result = invoke(runner, inherit, workspace, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_no_parent_reports(runner, workspace):
    result = invoke(runner, inherit, workspace, ["remove", "dev"])
    assert result.exit_code == 0
    assert "no parent" in result.output


def test_resolve_shows_merged_keys(runner, workspace):
    invoke(runner, inherit, workspace, ["set", "dev", "base"])
    result = invoke(runner, inherit, workspace, ["resolve", "dev"])
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=5432" in result.output
    assert "DEBUG=true" in result.output


def test_set_unknown_profile_exits_nonzero(runner, workspace):
    result = invoke(runner, inherit, workspace, ["set", "ghost", "base"])
    assert result.exit_code != 0
    assert "Error" in result.output
