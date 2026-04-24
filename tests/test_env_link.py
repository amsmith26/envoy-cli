"""Tests for envoy_cli.env_link."""

from __future__ import annotations

import pytest

from envoy_cli.env_link import (
    LinkError,
    add_link,
    get_links,
    remove_link,
    resolve_links,
)
from envoy_cli.vault import save_vault


PASSWORD = "test-secret"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "dev": {"DB_URL": "postgres://dev", "API_KEY": "dev-key"},
        "prod": {"DB_URL": "postgres://prod", "API_KEY": "prod-key"},
    }
    save_vault(path, PASSWORD, vault)
    return path


def test_add_link_success(vault_file):
    ref = add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    assert ref["src_profile"] == "prod"
    assert ref["src_key"] == "API_KEY"


def test_add_link_persisted(vault_file):
    add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    links = get_links(vault_file, PASSWORD)
    assert "dev" in links
    assert links["dev"]["API_KEY"]["src_profile"] == "prod"


def test_add_link_unknown_profile_raises(vault_file):
    with pytest.raises(LinkError, match="Profile 'staging' not found"):
        add_link(vault_file, PASSWORD, "staging", "API_KEY", "prod", "API_KEY")


def test_add_link_unknown_src_profile_raises(vault_file):
    with pytest.raises(LinkError, match="Source profile 'staging' not found"):
        add_link(vault_file, PASSWORD, "dev", "API_KEY", "staging", "API_KEY")


def test_add_link_unknown_key_raises(vault_file):
    with pytest.raises(LinkError, match="Key 'MISSING' not found in profile 'dev'"):
        add_link(vault_file, PASSWORD, "dev", "MISSING", "prod", "API_KEY")


def test_add_link_unknown_src_key_raises(vault_file):
    with pytest.raises(LinkError, match="Key 'MISSING' not found in profile 'prod'"):
        add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "MISSING")


def test_remove_link_returns_true(vault_file):
    add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    result = remove_link(vault_file, PASSWORD, "dev", "API_KEY")
    assert result is True


def test_remove_link_not_present_returns_false(vault_file):
    result = remove_link(vault_file, PASSWORD, "dev", "API_KEY")
    assert result is False


def test_remove_link_removes_from_store(vault_file):
    add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    remove_link(vault_file, PASSWORD, "dev", "API_KEY")
    links = get_links(vault_file, PASSWORD)
    assert "API_KEY" not in links.get("dev", {})


def test_resolve_links_substitutes_value(vault_file):
    add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    env = resolve_links(vault_file, PASSWORD, "dev")
    assert env["API_KEY"] == "prod-key"


def test_resolve_links_unlinked_key_unchanged(vault_file):
    add_link(vault_file, PASSWORD, "dev", "API_KEY", "prod", "API_KEY")
    env = resolve_links(vault_file, PASSWORD, "dev")
    assert env["DB_URL"] == "postgres://dev"


def test_resolve_links_unknown_profile_raises(vault_file):
    with pytest.raises(LinkError, match="Profile 'staging' not found"):
        resolve_links(vault_file, PASSWORD, "staging")


def test_get_links_empty_initially(vault_file):
    links = get_links(vault_file, PASSWORD)
    assert links == {}
