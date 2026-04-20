"""Tests for envoy_cli.lock"""

import pytest
from envoy_cli.lock import (
    LockError,
    get_locked_profiles,
    lock_profile,
    unlock_profile,
    is_locked,
    assert_unlocked,
    LOCK_KEY,
)


@pytest.fixture
def vault():
    return {
        "production": {"DB_URL": "postgres://prod"},
        "staging": {"DB_URL": "postgres://staging"},
    }


def test_get_locked_profiles_empty(vault):
    assert get_locked_profiles(vault) == []


def test_lock_profile_adds_to_list(vault):
    lock_profile(vault, "production")
    assert "production" in vault[LOCK_KEY]


def test_lock_profile_returns_sorted_list(vault):
    lock_profile(vault, "staging")
    lock_profile(vault, "production")
    assert vault[LOCK_KEY] == ["production", "staging"]


def test_lock_nonexistent_profile_raises(vault):
    with pytest.raises(LockError, match="does not exist"):
        lock_profile(vault, "ghost")


def test_lock_duplicate_no_duplicates(vault):
    lock_profile(vault, "production")
    lock_profile(vault, "production")
    assert vault[LOCK_KEY].count("production") == 1


def test_unlock_profile_removes_from_list(vault):
    lock_profile(vault, "production")
    unlock_profile(vault, "production")
    assert "production" not in vault.get(LOCK_KEY, [])


def test_unlock_not_locked_is_noop(vault):
    result = unlock_profile(vault, "staging")
    assert "staging" not in result


def test_is_locked_true(vault):
    lock_profile(vault, "production")
    assert is_locked(vault, "production") is True


def test_is_locked_false(vault):
    assert is_locked(vault, "staging") is False


def test_assert_unlocked_passes_when_not_locked(vault):
    assert_unlocked(vault, "staging")  # should not raise


def test_assert_unlocked_raises_when_locked(vault):
    lock_profile(vault, "production")
    with pytest.raises(LockError, match="locked"):
        assert_unlocked(vault, "production")
