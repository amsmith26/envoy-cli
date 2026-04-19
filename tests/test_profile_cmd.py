import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.commands.profile_cmd import profile
from envoy_cli.sync import push_env
from envoy_cli.vault import vault_exists

PASSWORD = "testpass"


@pytest.fixture
def workspace(tmp_path):
    vault = str(tmp_path / "test.vault")
    env_data = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}
    push_env(vault, "prod", env_data, PASSWORD)
    return {"vault": vault, "env_data": env_data}


@pytest.fixture
def runner():
    return CliRunner()


def test_list_profiles(runner, workspace):
    result = runner.invoke(
        profile,
        ["list", workspace["vault"], "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "prod" in result.output


def test_list_profiles_no_vault(runner, tmp_path):
    fake_vault = str(tmp_path / "missing.vault")
    result = runner.invoke(
        profile,
        ["list", fake_vault, "--password", PASSWORD],
    )
    assert result.exit_code != 0


def test_copy_profile(runner, workspace):
    result = runner.invoke(
        profile,
        ["copy", workspace["vault"], "prod", "staging", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "staging" in result.output

    list_result = runner.invoke(
        profile,
        ["list", workspace["vault"], "--password", PASSWORD],
    )
    assert "prod" in list_result.output
    assert "staging" in list_result.output


def test_rename_profile(runner, workspace):
    result = runner.invoke(
        profile,
        ["rename", workspace["vault"], "prod", "production", "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "production" in result.output

    list_result = runner.invoke(
        profile,
        ["list", workspace["vault"], "--password", PASSWORD],
    )
    assert "production" in list_result.output
    assert "prod" not in list_result.output


def test_copy_missing_profile(runner, workspace):
    result = runner.invoke(
        profile,
        ["copy", workspace["vault"], "nonexistent", "new", "--password", PASSWORD],
    )
    assert result.exit_code != 0
