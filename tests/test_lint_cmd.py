"""Integration tests for lint CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.commands.lint_cmd import lint
from envoy_cli.vault import save_vault


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_lint_file_no_issues(workspace, runner):
    env_file = workspace / ".env"
    env_file.write_text("APP_NAME=myapp\nPORT=8080\n")
    result = runner.invoke(lint, ["file", str(env_file)])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_lint_file_empty_value(workspace, runner):
    env_file = workspace / ".env"
    env_file.write_text("APP_NAME=\nPORT=8080\n")
    result = runner.invoke(lint, ["file", str(env_file)])
    assert result.exit_code != 0
    assert "empty_value" in result.output


def test_lint_file_not_found(workspace, runner):
    result = runner.invoke(lint, ["file", str(workspace / "missing.env")])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_lint_file_duplicate_key(workspace, runner):
    env_file = workspace / ".env"
    env_file.write_text("APP=foo\nAPP=bar\n")
    result = runner.invoke(lint, ["file", str(env_file)])
    assert result.exit_code != 0
    assert "duplicate_key" in result.output


def test_lint_profile_no_issues(workspace, runner):
    vault_file = str(workspace / ".env.vault")
    save_vault(vault_file, "secret", {"production": {"APP_NAME": "myapp", "PORT": "8080"}})
    result = runner.invoke(lint, ["profile", "production", "--vault", vault_file, "--password", "secret"])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_lint_profile_empty_value(workspace, runner):
    vault_file = str(workspace / ".env.vault")
    save_vault(vault_file, "secret", {"staging": {"APP_NAME": "", "PORT": "9000"}})
    result = runner.invoke(lint, ["profile", "staging", "--vault", vault_file, "--password", "secret"])
    assert result.exit_code != 0
    assert "empty_value" in result.output


def test_lint_profile_missing_profile(workspace, runner):
    vault_file = str(workspace / ".env.vault")
    save_vault(vault_file, "secret", {"production": {"APP": "ok"}})
    result = runner.invoke(lint, ["profile", "ghost", "--vault", vault_file, "--password", "secret"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_lint_profile_wrong_password(workspace, runner):
    vault_file = str(workspace / ".env.vault")
    save_vault(vault_file, "secret", {"production": {"APP": "ok"}})
    result = runner.invoke(lint, ["profile", "production", "--vault", vault_file, "--password", "wrong"])
    assert result.exit_code != 0
