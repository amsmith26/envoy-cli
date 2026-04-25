"""Tests for envoy_cli.env_inherit."""

import json
import os
import pytest

from envoy_cli.vault import save_vault, load_vault
from envoy_cli.env_inherit import (
    InheritError,
    get_parent,
    set_parent,
    remove_parent,
    resolve_inherited,
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "profiles": {
            "base": {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"},
            "dev": {"DEBUG": "true", "SECRET": "dev-secret"},
            "prod": {"SECRET": "prod-secret"},
        }
    }
    save_vault(path, "pass", vault)
    return path


def test_set_parent_returns_parent_name(vault_file):
    result = set_parent(vault_file, "pass", "dev", "base")
    assert result == "base"


def test_set_parent_persisted(vault_file):
    set_parent(vault_file, "pass", "dev", "base")
    vault = load_vault(vault_file, "pass")
    assert get_parent(vault, "dev") == "base"


def test_set_parent_unknown_profile_raises(vault_file):
    with pytest.raises(InheritError, match="Profile 'ghost' does not exist"):
        set_parent(vault_file, "pass", "ghost", "base")


def test_set_parent_unknown_parent_raises(vault_file):
    with pytest.raises(InheritError, match="Parent profile 'ghost' does not exist"):
        set_parent(vault_file, "pass", "dev", "ghost")


def test_set_parent_self_raises(vault_file):
    with pytest.raises(InheritError, match="cannot inherit from itself"):
        set_parent(vault_file, "pass", "dev", "dev")


def test_remove_parent_returns_true(vault_file):
    set_parent(vault_file, "pass", "dev", "base")
    assert remove_parent(vault_file, "pass", "dev") is True


def test_remove_parent_no_parent_returns_false(vault_file):
    assert remove_parent(vault_file, "pass", "dev") is False


def test_remove_parent_clears_link(vault_file):
    set_parent(vault_file, "pass", "dev", "base")
    remove_parent(vault_file, "pass", "dev")
    vault = load_vault(vault_file, "pass")
    assert get_parent(vault, "dev") is None


def test_resolve_inherited_child_overrides_parent(vault_file):
    set_parent(vault_file, "pass", "dev", "base")
    vault = load_vault(vault_file, "pass")
    env = resolve_inherited(vault, "dev")
    assert env["DEBUG"] == "true"        # child overrides parent
    assert env["HOST"] == "localhost"    # inherited from base
    assert env["PORT"] == "5432"         # inherited from base
    assert env["SECRET"] == "dev-secret" # child-only key


def test_resolve_no_parent_returns_own_keys(vault_file):
    vault = load_vault(vault_file, "pass")
    env = resolve_inherited(vault, "base")
    assert env == {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_resolve_circular_raises(vault_file):
    set_parent(vault_file, "pass", "dev", "prod")
    set_parent(vault_file, "pass", "prod", "dev")
    vault = load_vault(vault_file, "pass")
    with pytest.raises(InheritError, match="Circular inheritance"):
        resolve_inherited(vault, "dev")
