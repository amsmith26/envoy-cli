"""Tests for envoy_cli.env_placeholder."""

from __future__ import annotations

import pytest

from envoy_cli.env_placeholder import (
    PlaceholderError,
    get_placeholder_keys,
    mark_placeholder,
    unmark_placeholder,
    get_placeholder_description,
    list_unset_placeholders,
)
from envoy_cli.vault import save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {"profiles": {"dev": {"API_KEY": "", "DB_URL": "postgres://localhost"}}}
    save_vault(path, "secret", data)
    return path


def test_get_placeholder_keys_empty(vault_file):
    keys = get_placeholder_keys(vault_file, "secret", "dev")
    assert keys == []


def test_mark_placeholder_returns_sorted_list(vault_file):
    result = mark_placeholder(vault_file, "secret", "dev", "API_KEY")
    assert result == ["API_KEY"]


def test_mark_placeholder_persisted(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "API_KEY", "Your API key here")
    keys = get_placeholder_keys(vault_file, "secret", "dev")
    assert "API_KEY" in keys


def test_mark_multiple_keys_sorted(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "DB_URL")
    mark_placeholder(vault_file, "secret", "dev", "API_KEY")
    keys = get_placeholder_keys(vault_file, "secret", "dev")
    assert keys == ["API_KEY", "DB_URL"]


def test_mark_placeholder_unknown_profile_raises(vault_file):
    with pytest.raises(PlaceholderError, match="Profile 'prod' not found"):
        mark_placeholder(vault_file, "secret", "prod", "API_KEY")


def test_mark_placeholder_unknown_key_raises(vault_file):
    with pytest.raises(PlaceholderError, match="Key 'MISSING' not found"):
        mark_placeholder(vault_file, "secret", "dev", "MISSING")


def test_get_placeholder_description_after_mark(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "API_KEY", "Set this to your API key")
    desc = get_placeholder_description(vault_file, "secret", "dev", "API_KEY")
    assert desc == "Set this to your API key"


def test_get_placeholder_description_unmarked_returns_none(vault_file):
    desc = get_placeholder_description(vault_file, "secret", "dev", "API_KEY")
    assert desc is None


def test_unmark_placeholder_removes_entry(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "API_KEY")
    remaining = unmark_placeholder(vault_file, "secret", "dev", "API_KEY")
    assert "API_KEY" not in remaining


def test_unmark_placeholder_not_marked_raises(vault_file):
    with pytest.raises(PlaceholderError, match="not marked as a placeholder"):
        unmark_placeholder(vault_file, "secret", "dev", "API_KEY")


def test_list_unset_placeholders_empty_value(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "API_KEY")
    unset = list_unset_placeholders(vault_file, "secret", "dev")
    assert "API_KEY" in unset


def test_list_unset_placeholders_set_value_excluded(vault_file):
    mark_placeholder(vault_file, "secret", "dev", "DB_URL")
    unset = list_unset_placeholders(vault_file, "secret", "dev")
    assert "DB_URL" not in unset
