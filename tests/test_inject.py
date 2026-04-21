"""Tests for envoy_cli.inject."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from envoy_cli.inject import InjectError, build_env, inject_and_run
from envoy_cli.vault import save_vault

PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / "test.vault"
    vault = {
        "production": {"APP_ENV": "prod", "DB_HOST": "db.prod", "PORT": "5432"},
        "staging": {"APP_ENV": "staging", "DB_HOST": "db.staging"},
    }
    save_vault(str(path), vault, PASSWORD)
    return path


def test_build_env_includes_os_environ(vault_file: Path) -> None:
    env = build_env(str(vault_file), PASSWORD, "production")
    # PATH is virtually always set in the test runner environment.
    assert "PATH" in env


def test_build_env_injects_profile_values(vault_file: Path) -> None:
    env = build_env(str(vault_file), PASSWORD, "production")
    assert env["APP_ENV"] == "prod"
    assert env["DB_HOST"] == "db.prod"
    assert env["PORT"] == "5432"


def test_build_env_key_filter(vault_file: Path) -> None:
    env = build_env(str(vault_file), PASSWORD, "production", keys=["APP_ENV"])
    assert env["APP_ENV"] == "prod"
    assert "DB_HOST" not in env or env.get("DB_HOST") != "db.prod"
    # DB_HOST and PORT should not be injected from vault
    assert "PORT" not in env or env.get("PORT") != "5432"


def test_build_env_missing_key_raises(vault_file: Path) -> None:
    with pytest.raises(InjectError, match="MISSING_KEY"):
        build_env(str(vault_file), PASSWORD, "production", keys=["MISSING_KEY"])


def test_build_env_missing_profile_raises(vault_file: Path) -> None:
    with pytest.raises(InjectError, match="nonexistent"):
        build_env(str(vault_file), PASSWORD, "nonexistent")


def test_build_env_no_override_preserves_existing(vault_file: Path, monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "local")
    env = build_env(str(vault_file), PASSWORD, "production", override=False)
    assert env["APP_ENV"] == "local"


def test_build_env_override_replaces_existing(vault_file: Path, monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "local")
    env = build_env(str(vault_file), PASSWORD, "production", override=True)
    assert env["APP_ENV"] == "prod"


def test_inject_and_run_returns_exit_code(vault_file: Path) -> None:
    code = inject_and_run(
        str(vault_file),
        PASSWORD,
        "production",
        command=[sys.executable, "-c", "import sys; sys.exit(0)"],
    )
    assert code == 0


def test_inject_and_run_env_visible_in_subprocess(vault_file: Path) -> None:
    code = inject_and_run(
        str(vault_file),
        PASSWORD,
        "production",
        command=[
            sys.executable,
            "-c",
            "import os, sys; sys.exit(0 if os.environ.get('APP_ENV') == 'prod' else 1)",
        ],
    )
    assert code == 0


def test_inject_and_run_empty_command_raises(vault_file: Path) -> None:
    with pytest.raises(InjectError, match="No command"):
        inject_and_run(str(vault_file), PASSWORD, "production", command=[])
