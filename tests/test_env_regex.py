"""Tests for envoy_cli.env_regex."""

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_regex import (
    RegexError,
    get_pattern,
    set_pattern,
    remove_pattern,
    list_patterns,
    validate_profile,
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "production": {
            "PORT": "8080",
            "APP_ENV": "prod",
            "SECRET": "abc123",
        }
    }
    save_vault(path, "password", data)
    return path


def test_set_pattern_returns_pattern(vault_file):
    result = set_pattern(vault_file, "password", "production", "PORT", r"\d+")
    assert result == r"\d+"


def test_set_pattern_persisted(vault_file):
    set_pattern(vault_file, "password", "production", "PORT", r"\d+")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    assert get_pattern(vault, "production", "PORT") == r"\d+"


def test_set_pattern_invalid_regex_raises(vault_file):
    with pytest.raises(RegexError, match="Invalid regex"):
        set_pattern(vault_file, "password", "production", "PORT", r"[unclosed")


def test_set_pattern_unknown_profile_raises(vault_file):
    with pytest.raises(RegexError, match="Profile"):
        set_pattern(vault_file, "password", "staging", "PORT", r"\d+")


def test_set_pattern_unknown_key_raises(vault_file):
    with pytest.raises(RegexError, match="Key"):
        set_pattern(vault_file, "password", "production", "MISSING", r"\d+")


def test_remove_pattern_returns_true(vault_file):
    set_pattern(vault_file, "password", "production", "PORT", r"\d+")
    result = remove_pattern(vault_file, "password", "production", "PORT")
    assert result is True


def test_remove_pattern_not_found_returns_false(vault_file):
    result = remove_pattern(vault_file, "password", "production", "PORT")
    assert result is False


def test_list_patterns_empty(vault_file):
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    assert list_patterns(vault, "production") == {}


def test_list_patterns_after_set(vault_file):
    set_pattern(vault_file, "password", "production", "PORT", r"\d+")
    set_pattern(vault_file, "password", "production", "APP_ENV", r"prod|staging")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    patterns = list_patterns(vault, "production")
    assert patterns["PORT"] == r"\d+"
    assert patterns["APP_ENV"] == r"prod|staging"


def test_validate_profile_no_violations(vault_file):
    set_pattern(vault_file, "password", "production", "PORT", r"\d+")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    violations = validate_profile(vault, "production")
    assert violations == []


def test_validate_profile_with_violation(vault_file):
    set_pattern(vault_file, "password", "production", "APP_ENV", r"staging")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    violations = validate_profile(vault, "production")
    assert len(violations) == 1
    key, value, pattern = violations[0]
    assert key == "APP_ENV"
    assert value == "prod"
    assert pattern == r"staging"


def test_validate_profile_no_patterns(vault_file):
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "password")
    assert validate_profile(vault, "production") == []
