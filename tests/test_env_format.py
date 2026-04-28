"""Tests for envoy_cli.env_format."""

from __future__ import annotations

import pytest
from envoy_cli.env_format import (
    FormatError,
    list_formats,
    get_format,
    set_format,
    remove_format,
    apply_format,
    format_profile,
)


@pytest.fixture
def vault():
    return {
        "production": {"APP_NAME": "  Hello World  ", "DB_HOST": "Localhost"},
    }


def test_list_formats_returns_sorted():
    fmts = list_formats()
    assert fmts == sorted(fmts)
    assert "uppercase" in fmts
    assert "slug" in fmts


def test_set_format_returns_format_name(vault):
    result = set_format(vault, "production", "APP_NAME", "strip")
    assert result == "strip"


def test_set_format_persisted(vault):
    set_format(vault, "production", "APP_NAME", "uppercase")
    assert get_format(vault, "production", "APP_NAME") == "uppercase"


def test_get_format_missing_returns_none(vault):
    assert get_format(vault, "production", "APP_NAME") is None


def test_set_format_unknown_profile_raises(vault):
    with pytest.raises(FormatError, match="Profile"):
        set_format(vault, "staging", "APP_NAME", "uppercase")


def test_set_format_unknown_key_raises(vault):
    with pytest.raises(FormatError, match="Key"):
        set_format(vault, "production", "MISSING_KEY", "uppercase")


def test_set_format_invalid_format_raises(vault):
    with pytest.raises(FormatError, match="Unknown format"):
        set_format(vault, "production", "APP_NAME", "camelcase")


def test_remove_format_returns_true(vault):
    set_format(vault, "production", "APP_NAME", "strip")
    assert remove_format(vault, "production", "APP_NAME") is True


def test_remove_format_not_set_returns_false(vault):
    assert remove_format(vault, "production", "APP_NAME") is False


def test_apply_format_uppercase():
    assert apply_format("hello", "uppercase") == "HELLO"


def test_apply_format_lowercase():
    assert apply_format("HELLO", "lowercase") == "hello"


def test_apply_format_strip():
    assert apply_format("  hello  ", "strip") == "hello"


def test_apply_format_title():
    assert apply_format("hello world", "title") == "Hello World"


def test_apply_format_slug():
    assert apply_format("Hello World!", "slug") == "hello-world"


def test_apply_format_unknown_raises():
    with pytest.raises(FormatError):
        apply_format("value", "nonexistent")


def test_format_profile_applies_rules(vault):
    set_format(vault, "production", "DB_HOST", "uppercase")
    changed = format_profile(vault, "production")
    assert "DB_HOST" in changed
    assert vault["production"]["DB_HOST"] == "LOCALHOST"


def test_format_profile_dry_run_does_not_persist(vault):
    set_format(vault, "production", "DB_HOST", "uppercase")
    changed = format_profile(vault, "production", dry_run=True)
    assert "DB_HOST" in changed
    assert vault["production"]["DB_HOST"] == "Localhost"  # unchanged


def test_format_profile_no_rules_returns_empty(vault):
    changed = format_profile(vault, "production")
    assert changed == {}


def test_format_profile_unknown_profile_raises(vault):
    with pytest.raises(FormatError, match="Profile"):
        format_profile(vault, "staging")
