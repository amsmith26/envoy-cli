"""Tests for envoy_cli.history."""

import pytest

from envoy_cli.history import (
    clear_history,
    get_key_history,
    get_profile_history,
    record_change,
)
from envoy_cli.vault import save_vault


PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, PASSWORD, {"production": {"API_KEY": "abc"}})
    return path


def test_record_change_creates_entry(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", "abc", "xyz")
    history = get_key_history(vault_file, PASSWORD, "production", "API_KEY")
    assert len(history) == 1
    assert history[0]["old"] == "abc"
    assert history[0]["new"] == "xyz"


def test_record_change_stores_timestamp(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", None, "hello")
    history = get_key_history(vault_file, PASSWORD, "production", "API_KEY")
    assert "timestamp" in history[0]
    assert "T" in history[0]["timestamp"]  # ISO format


def test_multiple_changes_ordered_oldest_first(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", "v1", "v2")
    record_change(vault_file, PASSWORD, "production", "API_KEY", "v2", "v3")
    history = get_key_history(vault_file, PASSWORD, "production", "API_KEY")
    assert len(history) == 2
    assert history[0]["old"] == "v1"
    assert history[1]["old"] == "v2"


def test_get_key_history_missing_key_returns_empty(vault_file):
    result = get_key_history(vault_file, PASSWORD, "production", "NONEXISTENT")
    assert result == []


def test_get_key_history_missing_profile_returns_empty(vault_file):
    result = get_key_history(vault_file, PASSWORD, "staging", "API_KEY")
    assert result == []


def test_get_profile_history_returns_all_keys(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", "a", "b")
    record_change(vault_file, PASSWORD, "production", "DB_URL", None, "postgres://")
    profile_hist = get_profile_history(vault_file, PASSWORD, "production")
    assert "API_KEY" in profile_hist
    assert "DB_URL" in profile_hist


def test_clear_history_single_key(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", "a", "b")
    record_change(vault_file, PASSWORD, "production", "DB_URL", None, "pg")
    clear_history(vault_file, PASSWORD, "production", key="API_KEY")
    assert get_key_history(vault_file, PASSWORD, "production", "API_KEY") == []
    assert len(get_key_history(vault_file, PASSWORD, "production", "DB_URL")) == 1


def test_clear_history_entire_profile(vault_file):
    record_change(vault_file, PASSWORD, "production", "API_KEY", "a", "b")
    record_change(vault_file, PASSWORD, "production", "DB_URL", None, "pg")
    clear_history(vault_file, PASSWORD, "production")
    assert get_profile_history(vault_file, PASSWORD, "production") == {}


def test_clear_history_nonexistent_profile_is_noop(vault_file):
    # Should not raise
    clear_history(vault_file, PASSWORD, "ghost")


def test_history_capped_at_max_entries(vault_file):
    from envoy_cli.history import _MAX_ENTRIES

    for i in range(_MAX_ENTRIES + 10):
        record_change(vault_file, PASSWORD, "production", "API_KEY", str(i), str(i + 1))

    history = get_key_history(vault_file, PASSWORD, "production", "API_KEY")
    assert len(history) == _MAX_ENTRIES
    # Most recent entries should be kept
    assert history[-1]["new"] == str(_MAX_ENTRIES + 10)
