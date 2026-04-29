"""Tests for envoy_cli.env_usage."""

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_usage import (
    UsageError,
    record_access,
    get_usage,
    get_profile_usage,
    reset_usage,
    top_keys,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    password = "secret"
    data = {
        "dev": {"DB_URL": "postgres://localhost", "DEBUG": "true"},
        "prod": {"DB_URL": "postgres://prod", "SECRET_KEY": "abc123"},
    }
    save_vault(str(path), password, data)
    return str(path), password


def test_record_access_increments_count(vault_file):
    path, pw = vault_file
    entry = record_access(path, pw, "dev", "DB_URL")
    assert entry["count"] == 1


def test_record_access_twice_counts_two(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DB_URL")
    entry = record_access(path, pw, "dev", "DB_URL")
    assert entry["count"] == 2


def test_record_access_sets_first_and_last(vault_file):
    path, pw = vault_file
    entry = record_access(path, pw, "dev", "DEBUG")
    assert entry["first_access"] is not None
    assert entry["last_access"] is not None
    assert entry["first_access"] == entry["last_access"]


def test_record_access_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(UsageError, match="Profile 'staging' not found"):
        record_access(path, pw, "staging", "DB_URL")


def test_record_access_unknown_key_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(UsageError, match="Key 'MISSING' not found"):
        record_access(path, pw, "dev", "MISSING")


def test_get_usage_none_before_record(vault_file):
    path, pw = vault_file
    result = get_usage(path, pw, "dev", "DB_URL")
    assert result is None


def test_get_usage_after_record(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DB_URL")
    result = get_usage(path, pw, "dev", "DB_URL")
    assert result is not None
    assert result["count"] == 1


def test_get_profile_usage_returns_all_keys(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DB_URL")
    record_access(path, pw, "dev", "DEBUG")
    stats = get_profile_usage(path, pw, "dev")
    assert "DB_URL" in stats
    assert "DEBUG" in stats


def test_get_profile_usage_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(UsageError, match="Profile 'ghost' not found"):
        get_profile_usage(path, pw, "ghost")


def test_reset_usage_returns_true_if_existed(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DB_URL")
    result = reset_usage(path, pw, "dev", "DB_URL")
    assert result is True


def test_reset_usage_clears_stats(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DB_URL")
    reset_usage(path, pw, "dev", "DB_URL")
    assert get_usage(path, pw, "dev", "DB_URL") is None


def test_reset_usage_returns_false_if_not_existed(vault_file):
    path, pw = vault_file
    result = reset_usage(path, pw, "dev", "DB_URL")
    assert result is False


def test_top_keys_returns_sorted_by_count(vault_file):
    path, pw = vault_file
    record_access(path, pw, "dev", "DEBUG")
    record_access(path, pw, "dev", "DB_URL")
    record_access(path, pw, "dev", "DB_URL")
    results = top_keys(path, pw, "dev", n=2)
    assert results[0]["key"] == "DB_URL"
    assert results[0]["count"] == 2
    assert results[1]["key"] == "DEBUG"


def test_top_keys_empty_returns_empty_list(vault_file):
    path, pw = vault_file
    results = top_keys(path, pw, "dev")
    assert results == []
