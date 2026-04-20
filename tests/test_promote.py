"""Tests for envoy_cli.promote module."""

import pytest
from click.testing import CliRunner
from envoy_cli.vault import save_vault, load_vault
from envoy_cli.promote import promote_profile, list_promotable_keys, PromoteError
from envoy_cli.lock import lock_profile, LockError
from envoy_cli.commands.promote_cmd import promote


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging.db", "APP_ENV": "staging"},
    }
    save_vault(path, "secret", data)
    return path


def test_promote_all_keys(vault_file):
    result = promote_profile(vault_file, "secret", source="dev", target="staging")
    assert "DB_HOST" in result["promoted"]
    assert "DB_PORT" in result["promoted"]
    assert "DEBUG" in result["promoted"]


def test_promote_values_written_to_target(vault_file):
    promote_profile(vault_file, "secret", source="dev", target="prod")
    vault = load_vault(vault_file, "secret")
    assert vault["prod"]["DB_HOST"] == "localhost"
    assert vault["prod"]["DB_PORT"] == "5432"


def test_promote_creates_target_if_missing(vault_file):
    promote_profile(vault_file, "secret", source="dev", target="newenv")
    vault = load_vault(vault_file, "secret")
    assert "newenv" in vault


def test_promote_specific_keys_only(vault_file):
    result = promote_profile(vault_file, "secret", source="dev", target="staging", keys=["DEBUG"])
    assert result["promoted"] == ["DEBUG"]


def test_promote_missing_key_goes_to_skipped(vault_file):
    result = promote_profile(vault_file, "secret", source="dev", target="staging", keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result["skipped"]
    assert result["promoted"] == []


def test_promote_no_overwrite_skips_existing(vault_file):
    result = promote_profile(vault_file, "secret", source="dev", target="staging", overwrite=False)
    assert "DB_HOST" in result["skipped"]
    vault = load_vault(vault_file, "secret")
    assert vault["staging"]["DB_HOST"] == "staging.db"  # unchanged


def test_promote_source_not_found_raises(vault_file):
    with pytest.raises(PromoteError, match="does not exist"):
        promote_profile(vault_file, "secret", source="ghost", target="staging")


def test_promote_locked_target_raises(vault_file):
    vault = load_vault(vault_file, "secret")
    lock_profile(vault, "staging")
    save_vault(vault_file, "secret", vault)
    with pytest.raises(LockError):
        promote_profile(vault_file, "secret", source="dev", target="staging")


def test_list_promotable_keys(vault_file):
    result = list_promotable_keys(vault_file, "secret", source="dev", target="staging")
    assert "DB_PORT" in result["new"]
    assert "DEBUG" in result["new"]
    assert "DB_HOST" in result["changed"]
    assert result["unchanged"] == []


def test_list_promotable_keys_source_missing_raises(vault_file):
    with pytest.raises(PromoteError):
        list_promotable_keys(vault_file, "secret", source="missing", target="staging")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def workspace(tmp_path):
    path = str(tmp_path / "w.vault")
    data = {
        "dev": {"KEY_A": "alpha", "KEY_B": "beta"},
        "prod": {"KEY_A": "old_alpha"},
    }
    save_vault(path, "pass", data)
    return path


def test_cli_promote_run(runner, workspace):
    result = runner.invoke(promote, ["run", "--vault", workspace, "--password", "pass", "dev", "prod"])
    assert result.exit_code == 0
    assert "KEY_B" in result.output


def test_cli_promote_preview(runner, workspace):
    result = runner.invoke(promote, ["preview", "--vault", workspace, "--password", "pass", "dev", "prod"])
    assert result.exit_code == 0
    assert "KEY_B" in result.output
    vault = load_vault(workspace, "pass")
    assert "KEY_B" not in vault["prod"]  # preview should not modify


def test_cli_promote_missing_source(runner, workspace):
    result = runner.invoke(promote, ["run", "--vault", workspace, "--password", "pass", "ghost", "prod"])
    assert result.exit_code != 0
    assert "does not exist" in result.output
