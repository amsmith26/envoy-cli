"""Tests for envoy_cli.env_prefix."""

import pytest

from envoy_cli.env_prefix import (
    PrefixError,
    filter_by_prefix,
    get_prefix,
    list_prefixed_profiles,
    remove_prefix,
    set_prefix,
    strip_prefix,
)


@pytest.fixture
def vault():
    return {
        "production": {
            "APP_HOST": "prod.example.com",
            "APP_PORT": "443",
            "DB_HOST": "db.prod.example.com",
            "DB_PORT": "5432",
        },
        "staging": {
            "APP_HOST": "staging.example.com",
            "LOG_LEVEL": "debug",
        },
    }


def test_set_prefix_returns_prefix(vault):
    result = set_prefix(vault, "production", "APP_")
    assert result == "APP_"


def test_set_prefix_persisted(vault):
    set_prefix(vault, "production", "APP_")
    assert get_prefix(vault, "production") == "APP_"


def test_get_prefix_missing_returns_none(vault):
    assert get_prefix(vault, "production") is None


def test_set_prefix_unknown_profile_raises(vault):
    with pytest.raises(PrefixError, match="not found"):
        set_prefix(vault, "nonexistent", "X_")


def test_remove_prefix(vault):
    set_prefix(vault, "production", "APP_")
    remove_prefix(vault, "production")
    assert get_prefix(vault, "production") is None


def test_remove_prefix_nonexistent_is_noop(vault):
    remove_prefix(vault, "production")  # should not raise


def test_filter_by_prefix_returns_matching_keys(vault):
    result = filter_by_prefix(vault, "production", "APP_")
    assert result == {"APP_HOST": "prod.example.com", "APP_PORT": "443"}


def test_filter_by_prefix_no_match_returns_empty(vault):
    result = filter_by_prefix(vault, "production", "MISSING_")
    assert result == {}


def test_filter_by_prefix_unknown_profile_raises(vault):
    with pytest.raises(PrefixError, match="not found"):
        filter_by_prefix(vault, "ghost", "APP_")


def test_filter_by_prefix_case_insensitive(vault):
    result = filter_by_prefix(vault, "production", "app_", case_sensitive=False)
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_strip_prefix_removes_prefix_from_keys(vault):
    result = strip_prefix(vault, "production", "APP_")
    assert result == {"HOST": "prod.example.com", "PORT": "443"}


def test_strip_prefix_values_preserved(vault):
    result = strip_prefix(vault, "production", "DB_")
    assert result["HOST"] == "db.prod.example.com"
    assert result["PORT"] == "5432"


def test_strip_prefix_case_insensitive(vault):
    result = strip_prefix(vault, "production", "app_", case_sensitive=False)
    assert "HOST" in result and "PORT" in result


def test_list_prefixed_profiles_empty(vault):
    assert list_prefixed_profiles(vault) == []


def test_list_prefixed_profiles_after_set(vault):
    set_prefix(vault, "production", "APP_")
    set_prefix(vault, "staging", "LOG_")
    assert list_prefixed_profiles(vault) == ["production", "staging"]
