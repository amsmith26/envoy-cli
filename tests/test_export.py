"""Tests for envoy_cli.export module and export command."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy_cli.export import export_env, export_as_shell, export_as_docker, export_as_json
from envoy_cli.vault import save_vault
from envoy_cli.commands.export_cmd import cmd_export_profile

SAMPLE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": 'has"quote'}


def test_export_as_shell():
    result = export_as_shell(SAMPLE)
    assert 'export DB_HOST="localhost"' in result
    assert 'export DB_PORT="5432"' in result
    assert 'has\\"quote' in result


def test_export_as_docker():
    result = export_as_docker(SAMPLE)
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_export_as_json():
    result = export_as_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["DB_HOST"] == "localhost"
    assert parsed["SECRET"] == 'has"quote'


def test_export_env_delegates_format():
    assert export_env(SAMPLE, "json") == export_as_json(SAMPLE)
    assert export_env(SAMPLE, "shell") == export_as_shell(SAMPLE)
    assert export_env(SAMPLE, "docker") == export_as_docker(SAMPLE)


def test_export_env_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE, "yaml")


@pytest.fixture()
def workspace(tmp_path):
    vault_file = tmp_path / ".env.vault"
    save_vault(vault_file, "secret", {"production": {"APP_ENV": "prod", "PORT": "80"}})
    return tmp_path, vault_file


def test_export_profile_stdout(workspace):
    _, vault_file = workspace
    runner = CliRunner()
    result = runner.invoke(cmd_export_profile, ["production", "--vault", str(vault_file), "--password", "secret", "--format", "shell"])
    assert result.exit_code == 0
    assert 'export APP_ENV="prod"' in result.output


def test_export_profile_to_file(workspace, tmp_path):
    _, vault_file = workspace
    out_file = tmp_path / "out.env"
    runner = CliRunner()
    result = runner.invoke(cmd_export_profile, ["production", "--vault", str(vault_file), "--password", "secret", "--format", "docker", "--output", str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "APP_ENV=prod" in content


def test_export_missing_profile(workspace):
    _, vault_file = workspace
    runner = CliRunner()
    result = runner.invoke(cmd_export_profile, ["staging", "--vault", str(vault_file), "--password", "secret"])
    assert result.exit_code != 0


def test_export_missing_vault(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cmd_export_profile, ["production", "--vault", str(tmp_path / "nope.vault"), "--password", "x"])
    assert result.exit_code != 0
