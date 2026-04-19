"""Tests for envoy_cli.tag module."""
import pytest
from envoy_cli.tag import add_tag, remove_tag, get_tags, list_profiles_by_tag, clear_tags, TagError


@pytest.fixture
def vault():
    return {
        "production": {"KEY": "val1"},
        "staging": {"KEY": "val2"},
    }


def test_add_tag_returns_tag_list(vault):
    result = add_tag(vault, "production", "critical")
    assert "critical" in result


def test_add_tag_persisted_in_vault(vault):
    add_tag(vault, "production", "critical")
    assert "critical" in vault["__tags__"]["production"]


def test_add_multiple_tags_sorted(vault):
    add_tag(vault, "production", "zebra")
    add_tag(vault, "production", "alpha")
    tags = get_tags(vault, "production")
    assert tags == sorted(tags)


def test_add_duplicate_tag_no_duplicates(vault):
    add_tag(vault, "staging", "infra")
    add_tag(vault, "staging", "infra")
    assert vault["__tags__"]["staging"].count("infra") == 1


def test_get_tags_empty_profile(vault):
    assert get_tags(vault, "staging") == []


def test_get_tags_after_add(vault):
    add_tag(vault, "staging", "dev")
    assert "dev" in get_tags(vault, "staging")


def test_remove_tag_success(vault):
    add_tag(vault, "production", "temp")
    remove_tag(vault, "production", "temp")
    assert "temp" not in get_tags(vault, "production")


def test_remove_tag_not_found_raises(vault):
    with pytest.raises(TagError, match="not found"):
        remove_tag(vault, "production", "nonexistent")


def test_list_profiles_by_tag(vault):
    add_tag(vault, "production", "live")
    add_tag(vault, "staging", "live")
    result = list_profiles_by_tag(vault, "live")
    assert "production" in result
    assert "staging" in result


def test_list_profiles_by_tag_no_match(vault):
    result = list_profiles_by_tag(vault, "unknown-tag")
    assert result == []


def test_clear_tags_removes_all(vault):
    add_tag(vault, "production", "a")
    add_tag(vault, "production", "b")
    clear_tags(vault, "production")
    assert get_tags(vault, "production") == []


def test_clear_tags_nonexistent_profile_no_error(vault):
    clear_tags(vault, "ghost")  # should not raise
