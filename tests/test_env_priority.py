"""Tests for envoy_cli.env_priority."""

from __future__ import annotations

import pytest

from envoy_cli.env_priority import (
    PriorityError,
    get_priority,
    list_priorities,
    remove_priority,
    resolve_priority_order,
    set_priority,
)
from envoy_cli.vault import save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, "secret", {"production": {"KEY": "val"}, "staging": {"KEY": "stg"}})
    return path


def test_set_priority_returns_value(vault_file):
    result = set_priority(vault_file, "secret", "production", 10)
    assert result == 10


def test_set_priority_persisted(vault_file):
    set_priority(vault_file, "secret", "production", 5)
    assert get_priority(vault_file, "secret", "production") == 5


def test_get_priority_missing_returns_none(vault_file):
    assert get_priority(vault_file, "secret", "staging") is None


def test_set_priority_unknown_profile_raises(vault_file):
    with pytest.raises(PriorityError, match="does not exist"):
        set_priority(vault_file, "secret", "nonexistent", 1)


def test_set_priority_negative_raises(vault_file):
    with pytest.raises(PriorityError, match="non-negative"):
        set_priority(vault_file, "secret", "production", -1)


def test_remove_priority_returns_true(vault_file):
    set_priority(vault_file, "secret", "production", 3)
    assert remove_priority(vault_file, "secret", "production") is True


def test_remove_priority_clears_value(vault_file):
    set_priority(vault_file, "secret", "production", 3)
    remove_priority(vault_file, "secret", "production")
    assert get_priority(vault_file, "secret", "production") is None


def test_remove_priority_not_set_returns_false(vault_file):
    assert remove_priority(vault_file, "secret", "staging") is False


def test_list_priorities_sorted_ascending(vault_file):
    set_priority(vault_file, "secret", "staging", 20)
    set_priority(vault_file, "secret", "production", 5)
    entries = list_priorities(vault_file, "secret")
    assert entries[0]["profile"] == "production"
    assert entries[1]["profile"] == "staging"


def test_list_priorities_empty(vault_file):
    assert list_priorities(vault_file, "secret") == []


def test_resolve_priority_order_ranked_first(vault_file):
    set_priority(vault_file, "secret", "staging", 1)
    order = resolve_priority_order(vault_file, "secret")
    assert order[0] == "staging"
    assert "production" in order


def test_resolve_priority_order_unranked_appended(vault_file):
    set_priority(vault_file, "secret", "production", 1)
    order = resolve_priority_order(vault_file, "secret")
    assert order[-1] == "staging"


def test_resolve_priority_order_all_unranked(vault_file):
    order = resolve_priority_order(vault_file, "secret")
    assert set(order) == {"production", "staging"}
