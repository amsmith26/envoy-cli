"""Integration tests for TTL CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.commands.ttl_cmd import ttl
from envoy_cli.vault import save_vault

PASSWORD = "clipass"


@pytest.fixture
def workspace(tmp_path):
    vault_path = str(tmp_path / "env.vault")
    save_vault(vault_path, PASSWORD, {"staging": {"TOKEN": "xyz", "HOST": "localhost"}})
    return vault_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, vault_path, *args):
    return runner.invoke(ttl, ["--vault-file", vault_path, "--password", PASSWORD, *args])


def test_set_and_get_ttl(runner, workspace):
    result = invoke(runner, workspace, "set", "staging", "TOKEN", "--seconds", "3600")
    assert result.exit_code == 0
    assert "Expires at" in result.output

    result = invoke(runner, workspace, "get", "staging", "TOKEN")
    assert result.exit_code == 0
    assert "TOKEN" in result.output


def test_get_ttl_not_set(runner, workspace):
    result = invoke(runner, workspace, "get", "staging", "TOKEN")
    assert result.exit_code == 0
    assert "No TTL set" in result.output


def test_remove_ttl_command(runner, workspace):
    invoke(runner, workspace, "set", "staging", "TOKEN", "--seconds", "500")
    result = invoke(runner, workspace, "remove", "staging", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_ttl_not_set(runner, workspace):
    result = invoke(runner, workspace, "remove", "staging", "TOKEN")
    assert result.exit_code == 0
    assert "No TTL was set" in result.output


def test_list_ttls_empty(runner, workspace):
    result = invoke(runner, workspace, "list", "staging")
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_list_ttls_shows_entries(runner, workspace):
    invoke(runner, workspace, "set", "staging", "TOKEN", "--seconds", "7200")
    invoke(runner, workspace, "set", "staging", "HOST", "--seconds", "1800")
    result = invoke(runner, workspace, "list", "staging")
    assert result.exit_code == 0
    assert "TOKEN" in result.output
    assert "HOST" in result.output


def test_set_ttl_unknown_profile_fails(runner, workspace):
    result = invoke(runner, workspace, "set", "prod", "TOKEN", "--seconds", "60")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_purge_no_expired(runner, workspace):
    invoke(runner, workspace, "set", "staging", "TOKEN", "--seconds", "3600")
    result = invoke(runner, workspace, "purge", "staging")
    assert result.exit_code == 0
    assert "No expired" in result.output
