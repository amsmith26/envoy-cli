import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.commands.import_cmd import cmd_import_profile
from envoy_cli.sync import pull_env


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_import_dotenv_file(workspace, runner):
    env_file = workspace / "sample.env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    vault = str(workspace / ".env.vault")

    result = runner.invoke(cmd_import_profile, [
        "dev", str(env_file),
        "--format", "dotenv",
        "--password", "secret",
        "--vault", vault
    ])
    assert result.exit_code == 0
    assert "Imported 2 key(s)" in result.output

    env = pull_env(vault, "dev", "secret")
    assert env["FOO"] == "bar"
    assert env["BAZ"] == "qux"


def test_import_json_file(workspace, runner):
    json_file = workspace / "vars.json"
    json_file.write_text(json.dumps({"KEY1": "val1", "KEY2": "val2"}))
    vault = str(workspace / ".env.vault")

    result = runner.invoke(cmd_import_profile, [
        "staging", str(json_file),
        "--format", "json",
        "--password", "pass123",
        "--vault", vault
    ])
    assert result.exit_code == 0
    assert "Imported 2 key(s)" in result.output

    env = pull_env(vault, "staging", "pass123")
    assert env["KEY1"] == "val1"


def test_import_with_key_filter(workspace, runner):
    env_file = workspace / "all.env"
    env_file.write_text("A=1\nB=2\nC=3\n")
    vault = str(workspace / ".env.vault")

    result = runner.invoke(cmd_import_profile, [
        "prod", str(env_file),
        "--keys", "A,C",
        "--password", "pw",
        "--vault", vault
    ])
    assert result.exit_code == 0
    assert "Imported 2 key(s)" in result.output

    env = pull_env(vault, "prod", "pw")
    assert "A" in env
    assert "C" in env
    assert "B" not in env


def test_import_missing_source(workspace, runner):
    vault = str(workspace / ".env.vault")
    result = runner.invoke(cmd_import_profile, [
        "dev", str(workspace / "nonexistent.env"),
        "--password", "secret",
        "--vault", vault
    ])
    assert result.exit_code != 0
