"""Tests for envoy_cli.env_status."""

import pytest

from envoy_cli.vault import save_vault, load_vault
from envoy_cli.env_status import (
    get_key_status,
    get_profile_status,
    summarize_profile_status,
    StatusError,
)


PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.env.vault"
    vault = {
        "production": {
            "API_KEY": "abc123",
            "DB_URL": "postgres://localhost/prod",
            "SECRET": "s3cr3t",
        },
        "__deprecated__": {"production": {"API_KEY": {"note": "use NEW_API_KEY"}}},
        "__readonly__": {"production": ["DB_URL"]},
        "__sensitive__": {"production": ["SECRET", "API_KEY"]},
        "__required__": {"production": ["DB_URL", "API_KEY"]},
        "__masks__": {"production": ["SECRET"]},
        "__expiry__": {"production": {"API_KEY": "2025-01-01T00:00:00"}},
    }
    save_vault(str(path), vault, PASSWORD)
    return str(path)


def test_get_key_status_basic(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "DB_URL")
    assert status["key"] == "DB_URL"
    assert status["profile"] == "production"
    assert status["value"] == "postgres://localhost/prod"


def test_get_key_status_deprecated(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "API_KEY")
    assert status["deprecated"] is True
    assert status["deprecation_note"] == "use NEW_API_KEY"


def test_get_key_status_not_deprecated(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "DB_URL")
    assert status["deprecated"] is False
    assert status["deprecation_note"] is None


def test_get_key_status_readonly(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "DB_URL")
    assert status["readonly"] is True


def test_get_key_status_sensitive(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "SECRET")
    assert status["sensitive"] is True


def test_get_key_status_masked(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "SECRET")
    assert status["masked"] is True


def test_get_key_status_expires_at(vault_file):
    status = get_key_status(vault_file, PASSWORD, "production", "API_KEY")
    assert status["expires_at"] == "2025-01-01T00:00:00"


def test_get_key_status_unknown_profile_raises(vault_file):
    with pytest.raises(StatusError, match="Profile 'staging' not found"):
        get_key_status(vault_file, PASSWORD, "staging", "API_KEY")


def test_get_key_status_unknown_key_raises(vault_file):
    with pytest.raises(StatusError, match="Key 'MISSING' not found"):
        get_key_status(vault_file, PASSWORD, "production", "MISSING")


def test_get_profile_status_returns_all_keys(vault_file):
    statuses = get_profile_status(vault_file, PASSWORD, "production")
    keys = [s["key"] for s in statuses]
    assert sorted(keys) == ["API_KEY", "DB_URL", "SECRET"]


def test_get_profile_status_unknown_profile_raises(vault_file):
    with pytest.raises(StatusError, match="Profile 'ghost' not found"):
        get_profile_status(vault_file, PASSWORD, "ghost")


def test_summarize_profile_status_counts(vault_file):
    summary = summarize_profile_status(vault_file, PASSWORD, "production")
    assert summary["total"] == 3
    assert summary["deprecated"] == 1
    assert summary["readonly"] == 1
    assert summary["sensitive"] == 2
    assert summary["required"] == 2
    assert summary["masked"] == 1
    assert summary["expiring"] == 1
