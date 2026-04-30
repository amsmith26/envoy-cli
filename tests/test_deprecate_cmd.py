import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.commands.encrypt_cmd import _prompt_password
from envoy_cli.env_deprecate_cmd import deprecate


PASSWORD = "test-secret"


@pytest.fixture
def workspace(tmp_path):
    vault_file = tmp_path / "test.vault"
    vault = {
        "profiles": {
            "production": {"DATABASE_URL": "postgres://prod", "OLD_KEY": "legacy"}
        }
    }
    save_vault(str(vault_file), PASSWORD, vault)
    return tmp_path, vault_file


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    _, vault_file = workspace
    return runner.invoke(
        deprecate,
        ["--vault-file", str(vault_file), "--password", PASSWORD] + list(args),
    )


def test_deprecate_key_success(runner, workspace):
    result = invoke(runner, workspace, "set", "production", "OLD_KEY", "--reason", "use NEW_KEY instead")
    assert result.exit_code == 0
    assert "Deprecated 'OLD_KEY'" in result.output
    assert "use NEW_KEY instead" in result.output


def test_deprecate_key_with_replacement(runner, workspace):
    result = invoke(
        runner, workspace, "set", "production", "OLD_KEY",
        "--reason", "outdated", "--replacement", "NEW_KEY"
    )
    assert result.exit_code == 0
    assert "Replacement: NEW_KEY" in result.output


def test_deprecate_unknown_key_fails(runner, workspace):
    result = invoke(runner, workspace, "set", "production", "NONEXISTENT")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_list_deprecations_after_set(runner, workspace):
    invoke(runner, workspace, "set", "production", "OLD_KEY", "--reason", "legacy")
    result = invoke(runner, workspace, "list", "production")
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output


def test_list_deprecations_empty(runner, workspace):
    result = invoke(runner, workspace, "list", "production")
    assert result.exit_code == 0
    assert "No deprecated keys" in result.output


def test_undeprecate_key(runner, workspace):
    invoke(runner, workspace, "set", "production", "OLD_KEY")
    result = invoke(runner, workspace, "unset", "production", "OLD_KEY")
    assert result.exit_code == 0
    assert "Removed deprecation" in result.output


def test_undeprecate_not_deprecated_fails(runner, workspace):
    result = invoke(runner, workspace, "unset", "production", "OLD_KEY")
    assert result.exit_code != 0
    assert "Error" in result.output
