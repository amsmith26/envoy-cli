"""Tests for envoy_cli.env_default module."""

import pytest
from envoy_cli.env_default import (
    set_default,
    get_default,
    remove_default,
    list_defaults,
    apply_defaults,
    DefaultError,
)


@pytest.fixture
def vault():
    return {
        "production": {"DB_HOST": "prod-db", "API_KEY": "secret"},
        "staging": {"DB_HOST": "stage-db"},
    }


def test_set_default_returns_value(vault):
    result = set_default(vault, "DB_HOST", "localhost")
    assert result == "localhost"


def test_set_default_persisted(vault):
    set_default(vault, "API_KEY", "default-key")
    assert vault["__defaults__"]["API_KEY"] == "default-key"


def test_set_default_unknown_key_raises(vault):
    with pytest.raises(DefaultError, match="not found in any profile"):
        set_default(vault, "NONEXISTENT", "value")


def test_get_default_after_set(vault):
    set_default(vault, "DB_HOST", "localhost")
    assert get_default(vault, "DB_HOST") == "localhost"


def test_get_default_missing_returns_none(vault):
    assert get_default(vault, "DB_HOST") is None


def test_remove_default_returns_true(vault):
    set_default(vault, "DB_HOST", "localhost")
    assert remove_default(vault, "DB_HOST") is True


def test_remove_default_not_found_returns_false(vault):
    assert remove_default(vault, "DB_HOST") is False


def test_remove_default_no_longer_present(vault):
    set_default(vault, "DB_HOST", "localhost")
    remove_default(vault, "DB_HOST")
    assert get_default(vault, "DB_HOST") is None


def test_list_defaults_empty(vault):
    assert list_defaults(vault) == {}


def test_list_defaults_returns_all(vault):
    set_default(vault, "DB_HOST", "localhost")
    set_default(vault, "API_KEY", "default-key")
    defaults = list_defaults(vault)
    assert defaults == {"DB_HOST": "localhost", "API_KEY": "default-key"}


def test_apply_defaults_fills_missing_keys(vault):
    set_default(vault, "API_KEY", "fallback-key")
    result = apply_defaults(vault, "staging")
    assert result["API_KEY"] == "fallback-key"
    assert result["DB_HOST"] == "stage-db"


def test_apply_defaults_profile_value_overrides_default(vault):
    set_default(vault, "DB_HOST", "default-db")
    result = apply_defaults(vault, "production")
    assert result["DB_HOST"] == "prod-db"


def test_apply_defaults_unknown_profile_raises(vault):
    with pytest.raises(DefaultError, match="not found"):
        apply_defaults(vault, "unknown")


def test_apply_defaults_no_defaults_returns_profile_as_is(vault):
    result = apply_defaults(vault, "production")
    assert result == {"DB_HOST": "prod-db", "API_KEY": "secret"}
