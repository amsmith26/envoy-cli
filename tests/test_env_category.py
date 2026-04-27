"""Tests for envoy_cli.env_category."""

import pytest

from envoy_cli.env_category import (
    CategoryError,
    get_category,
    list_by_category,
    list_uncategorized,
    remove_category,
    set_category,
)
from envoy_cli.vault import save_vault


PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, PASSWORD, {"production": {"KEY": "val"}, "staging": {"KEY": "val2"}})
    return path


def test_set_category_returns_name(vault_file):
    result = set_category(vault_file, PASSWORD, "production", "live")
    assert result == "live"


def test_set_category_persisted(vault_file):
    set_category(vault_file, PASSWORD, "production", "live")
    assert get_category(vault_file, PASSWORD, "production") == "live"


def test_set_category_strips_whitespace(vault_file):
    result = set_category(vault_file, PASSWORD, "staging", "  dev  ")
    assert result == "dev"
    assert get_category(vault_file, PASSWORD, "staging") == "dev"


def test_set_category_unknown_profile_raises(vault_file):
    with pytest.raises(CategoryError, match="does not exist"):
        set_category(vault_file, PASSWORD, "nonexistent", "live")


def test_set_category_empty_name_raises(vault_file):
    with pytest.raises(CategoryError, match="must not be empty"):
        set_category(vault_file, PASSWORD, "production", "   ")


def test_get_category_missing_returns_none(vault_file):
    assert get_category(vault_file, PASSWORD, "production") is None


def test_remove_category_returns_true(vault_file):
    set_category(vault_file, PASSWORD, "production", "live")
    assert remove_category(vault_file, PASSWORD, "production") is True


def test_remove_category_clears_value(vault_file):
    set_category(vault_file, PASSWORD, "production", "live")
    remove_category(vault_file, PASSWORD, "production")
    assert get_category(vault_file, PASSWORD, "production") is None


def test_remove_category_not_set_returns_false(vault_file):
    assert remove_category(vault_file, PASSWORD, "production") is False


def test_list_by_category_groups_correctly(vault_file):
    set_category(vault_file, PASSWORD, "production", "live")
    set_category(vault_file, PASSWORD, "staging", "live")
    result = list_by_category(vault_file, PASSWORD)
    assert "live" in result
    assert sorted(result["live"]) == ["production", "staging"]


def test_list_by_category_empty(vault_file):
    assert list_by_category(vault_file, PASSWORD) == {}


def test_list_uncategorized_returns_all_when_none_set(vault_file):
    result = list_uncategorized(vault_file, PASSWORD)
    assert "production" in result
    assert "staging" in result


def test_list_uncategorized_excludes_categorized(vault_file):
    set_category(vault_file, PASSWORD, "production", "live")
    result = list_uncategorized(vault_file, PASSWORD)
    assert "production" not in result
    assert "staging" in result


def test_list_uncategorized_sorted(vault_file):
    result = list_uncategorized(vault_file, PASSWORD)
    assert result == sorted(result)
