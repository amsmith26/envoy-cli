"""Tests for envoy_cli.env_visibility."""

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_visibility import (
    get_visibility,
    set_visibility,
    remove_visibility,
    list_visibility,
    filter_by_visibility,
    VisibilityError,
    VISIBILITY_LEVELS,
)


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    password = "pass"
    vault = {
        "dev": {"API_KEY": "abc", "DEBUG": "true", "SECRET_TOKEN": "xyz"},
        "prod": {"API_KEY": "prod-abc"},
    }
    save_vault(path, password, vault)
    return path, password


def test_get_visibility_unset_returns_none(vault_file):
    path, pw = vault_file
    assert get_visibility(path, pw, "dev", "API_KEY") is None


def test_set_visibility_returns_level(vault_file):
    path, pw = vault_file
    result = set_visibility(path, pw, "dev", "API_KEY", "private")
    assert result == "private"


def test_set_visibility_persisted(vault_file):
    path, pw = vault_file
    set_visibility(path, pw, "dev", "DEBUG", "public")
    assert get_visibility(path, pw, "dev", "DEBUG") == "public"


def test_set_visibility_all_levels_accepted(vault_file):
    path, pw = vault_file
    for level in VISIBILITY_LEVELS:
        result = set_visibility(path, pw, "dev", "API_KEY", level)
        assert result == level


def test_set_visibility_invalid_level_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(VisibilityError, match="Invalid visibility level"):
        set_visibility(path, pw, "dev", "API_KEY", "hidden")


def test_set_visibility_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(VisibilityError, match="Profile 'staging' not found"):
        set_visibility(path, pw, "staging", "API_KEY", "public")


def test_set_visibility_unknown_key_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(VisibilityError, match="Key 'MISSING' not found"):
        set_visibility(path, pw, "dev", "MISSING", "public")


def test_remove_visibility_returns_true(vault_file):
    path, pw = vault_file
    set_visibility(path, pw, "dev", "API_KEY", "secret")
    assert remove_visibility(path, pw, "dev", "API_KEY") is True


def test_remove_visibility_returns_false_when_not_set(vault_file):
    path, pw = vault_file
    assert remove_visibility(path, pw, "dev", "API_KEY") is False


def test_remove_visibility_clears_value(vault_file):
    path, pw = vault_file
    set_visibility(path, pw, "dev", "API_KEY", "internal")
    remove_visibility(path, pw, "dev", "API_KEY")
    assert get_visibility(path, pw, "dev", "API_KEY") is None


def test_list_visibility_empty(vault_file):
    path, pw = vault_file
    assert list_visibility(path, pw, "dev") == {}


def test_list_visibility_after_set(vault_file):
    path, pw = vault_file
    set_visibility(path, pw, "dev", "API_KEY", "private")
    set_visibility(path, pw, "dev", "DEBUG", "public")
    result = list_visibility(path, pw, "dev")
    assert result == {"API_KEY": "private", "DEBUG": "public"}


def test_filter_by_visibility_returns_matching_keys(vault_file):
    path, pw = vault_file
    set_visibility(path, pw, "dev", "API_KEY", "secret")
    set_visibility(path, pw, "dev", "SECRET_TOKEN", "secret")
    set_visibility(path, pw, "dev", "DEBUG", "public")
    result = filter_by_visibility(path, pw, "dev", "secret")
    assert result == ["API_KEY", "SECRET_TOKEN"]


def test_filter_by_visibility_invalid_level_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(VisibilityError, match="Invalid visibility level"):
        filter_by_visibility(path, pw, "dev", "classified")
