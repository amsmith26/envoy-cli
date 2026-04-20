"""Tests for envoy_cli.commands.merge_cmd."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.vault import save_vault, load_vault
from envoy_cli.commands.merge_cmd import merge

PASSWORD = "test-secret"


@pytest.fixture
def workspace(tmp_path):
    vault_path = tmp_path / "envoy.vault"
    vault = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging.db", "API_KEY": "s3cr3t"},
    }
    save_vault(str(vault_path), PASSWORD, vault)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_merge_run_adds_keys(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    result = runner.invoke(
        merge, ["run", "dev", "--into", "staging", "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Added" in result.output
    vault = load_vault(vault_path, PASSWORD)
    assert "DB_PORT" in vault["staging"]


def test_merge_run_overwrite_flag(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    result = runner.invoke(
        merge, ["run", "dev", "--into", "staging", "--overwrite",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    vault = load_vault(vault_path, PASSWORD)
    assert vault["staging"]["DB_HOST"] == "localhost"
    assert "Updated" in result.output


def test_merge_run_key_filter(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    result = runner.invoke(
        merge, ["run", "dev", "--into", "staging", "--keys", "DB_PORT",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    vault = load_vault(vault_path, PASSWORD)
    assert "DB_PORT" in vault["staging"]
    assert "DEBUG" not in vault["staging"]


def test_merge_run_nothing_to_merge(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    # First merge to populate staging fully
    runner.invoke(
        merge, ["run", "dev", "--into", "staging", "--overwrite",
                "--vault", vault_path, "--password", PASSWORD]
    )
    # Second merge should report nothing new
    result = runner.invoke(
        merge, ["run", "dev", "--into", "staging",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "up to date" in result.output


def test_merge_run_unknown_source(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    result = runner.invoke(
        merge, ["run", "ghost", "--into", "staging",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_merge_preview_shows_candidates(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    result = runner.invoke(
        merge, ["preview", "dev", "--into", "staging",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Would add" in result.output or "Would update" in result.output


def test_merge_preview_no_changes(workspace, runner):
    vault_path = str(workspace / "envoy.vault")
    # Make staging identical to dev first
    vault = load_vault(vault_path, PASSWORD)
    vault["staging"] = dict(vault["dev"])
    save_vault(vault_path, PASSWORD, vault)

    result = runner.invoke(
        merge, ["preview", "dev", "--into", "staging",
                "--vault", vault_path, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "No changes" in result.output
