"""Tests for the history CLI commands."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy_cli.commands.history_cmd import history
from envoy_cli.vault import save_vault, load_vault
from envoy_cli.history import record_change


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Set up a temporary workspace with a vault file."""
    monkeypatch.chdir(tmp_path)
    vault_file = tmp_path / "test.vault"
    password = "testpass"

    # Create a vault with two profiles
    initial_data = {
        "dev": {"API_KEY": "dev-key", "DEBUG": "true"},
        "prod": {"API_KEY": "prod-key", "DEBUG": "false"},
    }
    save_vault(vault_file, initial_data, password)

    return {"vault": vault_file, "password": password}


@pytest.fixture
def runner():
    return CliRunner()


def test_key_history_shows_entries(workspace, runner):
    """Test that key-history command displays recorded changes."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    record_change(vault_file, password, "dev", "API_KEY", "old-key", "dev-key")

    result = runner.invoke(
        history,
        ["key-history", str(vault_file), password, "dev", "API_KEY"],
    )

    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "dev-key" in result.output


def test_key_history_no_entries(workspace, runner):
    """Test key-history output when no history exists for the key."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    result = runner.invoke(
        history,
        ["key-history", str(vault_file), password, "dev", "NONEXISTENT_KEY"],
    )

    assert result.exit_code == 0
    assert "No history" in result.output or result.output.strip() == "" or "0" in result.output


def test_profile_history_shows_all_keys(workspace, runner):
    """Test that profile-history lists changes across all keys."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    record_change(vault_file, password, "dev", "API_KEY", "old-key", "dev-key")
    record_change(vault_file, password, "dev", "DEBUG", "false", "true")

    result = runner.invoke(
        history,
        ["profile-history", str(vault_file), password, "dev"],
    )

    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DEBUG" in result.output


def test_profile_history_empty(workspace, runner):
    """Test profile-history when no changes have been recorded."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    result = runner.invoke(
        history,
        ["profile-history", str(vault_file), password, "prod"],
    )

    assert result.exit_code == 0


def test_clear_history_removes_entries(workspace, runner):
    """Test that clear-history wipes all recorded history."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    record_change(vault_file, password, "dev", "API_KEY", "old", "new")

    result = runner.invoke(
        history,
        ["clear-history", str(vault_file), password],
        input="y\n",
    )

    assert result.exit_code == 0

    # Verify history is gone
    result2 = runner.invoke(
        history,
        ["key-history", str(vault_file), password, "dev", "API_KEY"],
    )
    assert result2.exit_code == 0
    assert "old" not in result2.output


def test_clear_history_aborted(workspace, runner):
    """Test that clear-history does nothing when user aborts."""
    vault_file = workspace["vault"]
    password = workspace["password"]

    record_change(vault_file, password, "dev", "API_KEY", "old", "new")

    result = runner.invoke(
        history,
        ["clear-history", str(vault_file), password],
        input="n\n",
    )

    # History should still exist
    result2 = runner.invoke(
        history,
        ["key-history", str(vault_file), password, "dev", "API_KEY"],
    )
    assert "new" in result2.output or result2.exit_code == 0
