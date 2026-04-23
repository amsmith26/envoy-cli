"""Integration tests for the validate CLI commands."""

import pytest
from click.testing import CliRunner

from envoy_cli.commands.validate_cmd import validate
from envoy_cli.vault import save_vault


@pytest.fixture
def workspace(tmp_path):
    vault = str(tmp_path / "test.vault")
    save_vault(vault, "secret", {"profiles": {"prod": {"PORT": "8080", "HOST": "localhost"}}})
    return {"vault": vault, "password": "secret"}


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, workspace, *args):
    return runner.invoke(
        validate,
        ["--vault-file", workspace["vault"], "--password", workspace["password"]] + list(args),
    )


def test_set_rule_and_list(runner, workspace):
    result = invoke(runner, workspace, "set-rule", "prod", "PORT", "--type", "int")
    assert result.exit_code == 0
    assert "Rule set" in result.output

    result = invoke(runner, workspace, "list-rules", "prod")
    assert "PORT" in result.output
    assert "int" in result.output


def test_set_rule_no_options_fails(runner, workspace):
    result = invoke(runner, workspace, "set-rule", "prod", "PORT")
    assert result.exit_code != 0


def test_set_rule_invalid_type(runner, workspace):
    result = invoke(runner, workspace, "set-rule", "prod", "PORT", "--type", "uuid")
    assert result.exit_code != 0
    assert "Unsupported type" in result.output


def test_remove_rule(runner, workspace):
    invoke(runner, workspace, "set-rule", "prod", "PORT", "--type", "int")
    result = invoke(runner, workspace, "remove-rule", "prod", "PORT")
    assert "Rule removed" in result.output


def test_remove_rule_nonexistent(runner, workspace):
    result = invoke(runner, workspace, "remove-rule", "prod", "PORT")
    assert "No rule found" in result.output


def test_run_validation_passes(runner, workspace):
    invoke(runner, workspace, "set-rule", "prod", "PORT", "--type", "int")
    result = invoke(runner, workspace, "run", "prod")
    assert result.exit_code == 0
    assert "passed" in result.output


def test_run_validation_fails(runner, workspace):
    from envoy_cli.vault import load_vault, save_vault as sv
    vault = load_vault(workspace["vault"], "secret")
    vault["profiles"]["prod"]["PORT"] = "not_a_number"
    sv(workspace["vault"], "secret", vault)
    invoke(runner, workspace, "set-rule", "prod", "PORT", "--type", "int")
    result = invoke(runner, workspace, "run", "prod")
    assert result.exit_code == 1
    assert "PORT" in result.output


def test_list_rules_empty(runner, workspace):
    result = invoke(runner, workspace, "list-rules", "prod")
    assert "No validation rules" in result.output
