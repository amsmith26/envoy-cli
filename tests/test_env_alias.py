"""Tests for envoy_cli.env_alias."""

import pytest

from envoy_cli.env_alias import (
    AliasError,
    add_alias,
    get_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
)
from envoy_cli.vault import save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "dev": {"DATABASE_URL": "postgres://localhost/dev", "SECRET": "abc123"},
        "prod": {"DATABASE_URL": "postgres://prod/db"},
    }
    save_vault(vault, path, "pass")
    return path


def test_add_alias_returns_target_key(vault_file):
    target = add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    assert target == "DATABASE_URL"


def test_add_alias_persisted(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    aliases = list_aliases(vault_file, "pass", "dev")
    assert aliases["DB"] == "DATABASE_URL"


def test_add_multiple_aliases(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    add_alias(vault_file, "pass", "dev", "SEC", "SECRET")
    aliases = list_aliases(vault_file, "pass", "dev")
    assert len(aliases) == 2
    assert aliases["SEC"] == "SECRET"


def test_add_alias_unknown_profile_raises(vault_file):
    with pytest.raises(AliasError, match="Profile"):
        add_alias(vault_file, "pass", "staging", "DB", "DATABASE_URL")


def test_add_alias_unknown_key_raises(vault_file):
    with pytest.raises(AliasError, match="Key"):
        add_alias(vault_file, "pass", "dev", "ALIAS", "NONEXISTENT")


def test_add_alias_conflicts_with_real_key_raises(vault_file):
    with pytest.raises(AliasError, match="already exists"):
        add_alias(vault_file, "pass", "dev", "SECRET", "DATABASE_URL")


def test_remove_alias_returns_true(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    result = remove_alias(vault_file, "pass", "dev", "DB")
    assert result is True


def test_remove_alias_not_found_returns_false(vault_file):
    result = remove_alias(vault_file, "pass", "dev", "GHOST")
    assert result is False


def test_remove_alias_is_gone_after_removal(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    remove_alias(vault_file, "pass", "dev", "DB")
    aliases = list_aliases(vault_file, "pass", "dev")
    assert "DB" not in aliases


def test_resolve_alias_returns_value(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    value = resolve_alias(vault_file, "pass", "dev", "DB")
    assert value == "postgres://localhost/dev"


def test_resolve_alias_not_found_returns_none(vault_file):
    result = resolve_alias(vault_file, "pass", "dev", "GHOST")
    assert result is None


def test_get_aliases_returns_all_profiles(vault_file):
    add_alias(vault_file, "pass", "dev", "DB", "DATABASE_URL")
    add_alias(vault_file, "pass", "prod", "DB", "DATABASE_URL")
    all_aliases = get_aliases(vault_file, "pass")
    assert "dev" in all_aliases
    assert "prod" in all_aliases


def test_list_aliases_empty_profile(vault_file):
    aliases = list_aliases(vault_file, "pass", "prod")
    assert aliases == {}
