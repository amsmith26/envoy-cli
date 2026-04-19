"""Tests for audit logging."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envoy_cli.audit import record_event, get_log, clear_log, _audit_path
from envoy_cli.commands.audit_cmd import audit


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    return tmp_path / "project.env.vault"


def test_record_and_get_log(vault_file: Path) -> None:
    record_event(vault_file, "push", "production", "3 keys")
    entries = get_log(vault_file)
    assert len(entries) == 1
    assert entries[0]["action"] == "push"
    assert entries[0]["profile"] == "production"
    assert entries[0]["details"] == "3 keys"


def test_multiple_events_appended(vault_file: Path) -> None:
    record_event(vault_file, "push", "staging")
    record_event(vault_file, "pull", "staging")
    record_event(vault_file, "delete", "staging")
    entries = get_log(vault_file)
    assert len(entries) == 3
    assert [e["action"] for e in entries] == ["push", "pull", "delete"]


def test_get_log_no_file(vault_file: Path) -> None:
    entries = get_log(vault_file)
    assert entries == []


def test_clear_log(vault_file: Path) -> None:
    record_event(vault_file, "push", "dev")
    clear_log(vault_file)
    assert not _audit_path(vault_file).exists()
    assert get_log(vault_file) == []


def test_log_is_valid_json(vault_file: Path) -> None:
    record_event(vault_file, "push", "prod", "5 keys")
    raw = _audit_path(vault_file).read_text()
    data = json.loads(raw)
    assert isinstance(data, list)


def test_cmd_show_log(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")
    from envoy_cli.vault import _vault_path
    vault = _vault_path(str(env_file))
    record_event(vault, "push", "prod")
    runner = CliRunner()
    result = runner.invoke(audit, ["log", "--env-file", str(env_file)])
    assert result.exit_code == 0
    assert "push" in result.output


def test_cmd_show_log_filter_profile(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")
    from envoy_cli.vault import _vault_path
    vault = _vault_path(str(env_file))
    record_event(vault, "push", "prod")
    record_event(vault, "push", "staging")
    runner = CliRunner()
    result = runner.invoke(audit, ["log", "--env-file", str(env_file), "--profile", "staging"])
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "prod" not in result.output
