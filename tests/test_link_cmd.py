"""Integration tests for the 'link' CLI command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.commands.link_cmd import link
from envoy_cli.vault import save_vault


PASSWORD = "cli-secret"


@pytest.fixture()
def workspace(tmp_path):
    vault_path = str(tmp_path / "test.vault")
    vault = {
        "dev": {"DB_URL": "postgres://dev", "API_KEY": "dev-key"},
        "prod": {"DB_URL": "postgres://prod", "API_KEY": "prod-key"},
    }
    save_vault(vault_path, PASSWORD, vault)
    return vault_path


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(
        link,
        ["--vault", workspace, "--password", PASSWORD, *args],
    )


def test_add_link_command(runner, workspace):
    result = invoke(runner, workspace, "add", "dev", "API_KEY", "prod", "API_KEY")
    assert result.exit_code == 0
    assert "Linked dev.API_KEY -> prod.API_KEY" in result.output


def test_list_links_after_add(runner, workspace):
    invoke(runner, workspace, "add", "dev", "API_KEY", "prod", "API_KEY")
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "API_KEY -> prod.API_KEY" in result.output


def test_list_links_empty(runner, workspace):
    result = invoke(runner, workspace, "list", "dev")
    assert result.exit_code == 0
    assert "No links defined" in result.output


def test_remove_link_command(runner, workspace):
    invoke(runner, workspace, "add", "dev", "API_KEY", "prod", "API_KEY")
    result = invoke(runner, workspace, "remove", "dev", "API_KEY")
    assert result.exit_code == 0
    assert "Link removed" in result.output


def test_remove_link_not_found(runner, workspace):
    result = invoke(runner, workspace, "remove", "dev", "API_KEY")
    assert result.exit_code != 0
    assert "No link found" in result.output


def test_resolve_links_command(runner, workspace):
    invoke(runner, workspace, "add", "dev", "API_KEY", "prod", "API_KEY")
    result = invoke(runner, workspace, "resolve", "dev")
    assert result.exit_code == 0
    assert "API_KEY=prod-key" in result.output
    assert "DB_URL=postgres://dev" in result.output


def test_add_link_unknown_profile_exits(runner, workspace):
    result = invoke(runner, workspace, "add", "staging", "API_KEY", "prod", "API_KEY")
    assert result.exit_code != 0
    assert "Error" in result.output
