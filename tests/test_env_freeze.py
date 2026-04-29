"""Tests for envoy_cli.env_freeze."""
import pytest

from envoy_cli.env_freeze import (
    FreezeError,
    assert_not_frozen,
    freeze_profile,
    get_frozen_profiles,
    is_frozen,
    unfreeze_profile,
)
from envoy_cli.vault import save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    password = "secret"
    vault = {
        "production": {"DB_URL": "postgres://prod"},
        "staging": {"DB_URL": "postgres://staging"},
    }
    save_vault(path, password, vault)
    return path, password


def test_get_frozen_profiles_empty(vault_file):
    path, pw = vault_file
    assert get_frozen_profiles(path, pw) == []


def test_freeze_profile_returns_sorted_list(vault_file):
    path, pw = vault_file
    result = freeze_profile(path, pw, "production")
    assert result == ["production"]


def test_freeze_profile_persisted(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "staging")
    assert "staging" in get_frozen_profiles(path, pw)


def test_freeze_multiple_profiles_sorted(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "staging")
    freeze_profile(path, pw, "production")
    assert get_frozen_profiles(path, pw) == ["production", "staging"]


def test_freeze_duplicate_no_duplicates(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "production")
    freeze_profile(path, pw, "production")
    assert get_frozen_profiles(path, pw).count("production") == 1


def test_freeze_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(FreezeError, match="not found"):
        freeze_profile(path, pw, "nonexistent")


def test_unfreeze_profile_removes_entry(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "production")
    remaining = unfreeze_profile(path, pw, "production")
    assert "production" not in remaining


def test_unfreeze_not_frozen_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(FreezeError, match="not frozen"):
        unfreeze_profile(path, pw, "production")


def test_is_frozen_true(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "production")
    assert is_frozen(path, pw, "production") is True


def test_is_frozen_false(vault_file):
    path, pw = vault_file
    assert is_frozen(path, pw, "staging") is False


def test_assert_not_frozen_passes_when_unfrozen(vault_file):
    path, pw = vault_file
    assert_not_frozen(path, pw, "production")  # should not raise


def test_assert_not_frozen_raises_when_frozen(vault_file):
    path, pw = vault_file
    freeze_profile(path, pw, "production")
    with pytest.raises(FreezeError, match="frozen"):
        assert_not_frozen(path, pw, "production")
