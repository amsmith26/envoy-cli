"""Tests for envoy_cli.commands.transform_cmd."""

import pytest
from click.testing import CliRunner
from envoy_cli.vault import save_vault
from envoy_cli.commands.transform_cmd import transform


@pytest.fixture
def workspace(tmp_path):
    vault = str(tmp_path / "test.vault")
    data = {"dev": {"APP_NAME": "hello", "DB_URL": "localhost"}}
    save_vault(vault, "secret", data)
    return {"vault": vault, "password": "secret"}


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(
        transform,
        ["--vault", workspace["vault"], "--password", workspace["password"], *args],
    )


def test_transform_key_command(runner, workspace):
    result = invoke(runner, workspace, "key", "dev", "APP_NAME", "upper")
    assert result.exit_code == 0
    assert "'hello'" in result.output
    assert "'HELLO'" in result.output


def test_transform_key_dry_run(runner, workspace):
    result = invoke(runner, workspace, "key", "dev", "APP_NAME", "upper", "--dry-run")
    assert result.exit_code == 0
    assert "[dry-run]" in result.output
    # value unchanged
    result2 = invoke(runner, workspace, "key", "dev", "APP_NAME", "upper")
    assert "'hello'" in result2.output


def test_transform_profile_command(runner, workspace):
    result = invoke(runner, workspace, "profile", "dev", "upper")
    assert result.exit_code == 0
    assert "Transformed 2 key(s)" in result.output


def test_transform_profile_with_key_filter(runner, workspace):
    result = invoke(runner, workspace, "profile", "dev", "upper", "--key", "APP_NAME")
    assert result.exit_code == 0
    assert "Transformed 1 key(s)" in result.output


def test_transform_unknown_raises_error(runner, workspace):
    result = invoke(runner, workspace, "key", "dev", "APP_NAME", "bogus")
    assert result.exit_code != 0
    assert "Unknown transform" in result.output


def test_preview_command(runner, workspace):
    result = runner.invoke(transform, ["preview", "hello world", "urlencode"])
    assert result.exit_code == 0
    assert "hello%20world" in result.output


def test_list_command(runner, workspace):
    result = runner.invoke(transform, ["list"])
    assert result.exit_code == 0
    assert "upper" in result.output
    assert "lower" in result.output
    assert "base64encode" in result.output
