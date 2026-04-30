"""Tests for envoy_cli.env_namespace."""

import pytest

from envoy_cli.env_namespace import (
    NamespaceError,
    get_namespace,
    get_profiles_in_namespace,
    list_namespaces,
    remove_namespace,
    set_namespace,
)
from envoy_cli.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    password = "secret"
    vault = {
        "dev": {"APP_HOST": "localhost"},
        "prod": {"APP_HOST": "example.com"},
        "staging": {"APP_HOST": "staging.example.com"},
    }
    save_vault(str(path), password, vault)
    return str(path), password


def test_list_namespaces_empty(vault_file):
    path, pw = vault_file
    assert list_namespaces(path, pw) == []


def test_set_namespace_returns_name(vault_file):
    path, pw = vault_file
    result = set_namespace(path, pw, "dev", "backend")
    assert result == "backend"


def test_set_namespace_persisted(vault_file):
    path, pw = vault_file
    set_namespace(path, pw, "dev", "backend")
    assert get_namespace(path, pw, "dev") == "backend"


def test_get_namespace_missing_returns_none(vault_file):
    path, pw = vault_file
    assert get_namespace(path, pw, "dev") is None


def test_set_namespace_unknown_profile_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(NamespaceError, match="not found"):
        set_namespace(path, pw, "ghost", "backend")


def test_set_namespace_empty_name_raises(vault_file):
    path, pw = vault_file
    with pytest.raises(NamespaceError, match="empty"):
        set_namespace(path, pw, "dev", "   ")


def test_list_namespaces_after_set(vault_file):
    path, pw = vault_file
    set_namespace(path, pw, "dev", "backend")
    set_namespace(path, pw, "prod", "frontend")
    assert list_namespaces(path, pw) == ["backend", "frontend"]


def test_get_profiles_in_namespace(vault_file):
    path, pw = vault_file
    set_namespace(path, pw, "dev", "backend")
    set_namespace(path, pw, "staging", "backend")
    set_namespace(path, pw, "prod", "frontend")
    result = get_profiles_in_namespace(path, pw, "backend")
    assert result == ["dev", "staging"]


def test_get_profiles_in_namespace_empty(vault_file):
    path, pw = vault_file
    assert get_profiles_in_namespace(path, pw, "nonexistent") == []


def test_remove_namespace_returns_true(vault_file):
    path, pw = vault_file
    set_namespace(path, pw, "dev", "backend")
    assert remove_namespace(path, pw, "dev") is True


def test_remove_namespace_not_set_returns_false(vault_file):
    path, pw = vault_file
    assert remove_namespace(path, pw, "dev") is False


def test_remove_namespace_clears_assignment(vault_file):
    path, pw = vault_file
    set_namespace(path, pw, "dev", "backend")
    remove_namespace(path, pw, "dev")
    assert get_namespace(path, pw, "dev") is None
