"""Tests for envoy_cli.search module."""

import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.search import search_by_key, search_by_value, search_env

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    data = {
        "production": {
            "DATABASE_URL": "postgres://prod",
            "SECRET_KEY": "abc123",
            "DEBUG": "false",
        },
        "staging": {
            "DATABASE_URL": "postgres://staging",
            "DEBUG": "true",
            "API_KEY": "staging-secret",
        },
    }
    save_vault(str(path), PASSWORD, data)
    return str(path)


def test_search_by_key_finds_match(vault_file):
    results = search_by_key(vault_file, PASSWORD, "DATABASE")
    assert "production" in results
    assert "staging" in results
    assert "DATABASE_URL" in results["production"]


def test_search_by_key_no_match(vault_file):
    results = search_by_key(vault_file, PASSWORD, "NONEXISTENT")
    assert results == {}


def test_search_by_key_case_insensitive(vault_file):
    results = search_by_key(vault_file, PASSWORD, "database_url", case_sensitive=False)
    assert "production" in results


def test_search_by_key_case_sensitive_no_match(vault_file):
    results = search_by_key(vault_file, PASSWORD, "database_url", case_sensitive=True)
    assert results == {}


def test_search_by_value_finds_match(vault_file):
    results = search_by_value(vault_file, PASSWORD, "postgres")
    assert "production" in results
    assert "staging" in results


def test_search_by_value_single_profile(vault_file):
    results = search_by_value(vault_file, PASSWORD, "abc123")
    assert "production" in results
    assert "staging" not in results


def test_search_by_value_no_match(vault_file):
    results = search_by_value(vault_file, PASSWORD, "nope")
    assert results == {}


def test_search_env_key_mode(vault_file):
    results = search_env(vault_file, PASSWORD, "SECRET", mode="key")
    assert "production" in results


def test_search_env_value_mode(vault_file):
    results = search_env(vault_file, PASSWORD, "staging-secret", mode="value")
    assert "staging" in results


def test_search_env_invalid_mode(vault_file):
    with pytest.raises(ValueError, match="Unknown search mode"):
        search_env(vault_file, PASSWORD, "x", mode="invalid")
