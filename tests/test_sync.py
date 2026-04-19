"""Tests for envoy_cli.sync module."""

import pytest
from pathlib import Path

from envoy_cli.sync import push_env, pull_env, list_profiles, delete_profile


PASSWORD = "test-secret"


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_NAME=envoy\nDEBUG=true\n")
    return f


@pytest.fixture
def vault_file(tmp_path):
    return tmp_path / ".env.vault"


def test_push_creates_profile(env_file, vault_file):
    push_env(env_file, vault_file, PASSWORD, "production")
    profiles = list_profiles(vault_file, PASSWORD)
    assert "production" in profiles


def test_push_stores_correct_values(env_file, vault_file):
    push_env(env_file, vault_file, PASSWORD, "staging")
    from envoy_cli.vault import load_vault
    data = load_vault(vault_file, PASSWORD)
    assert data["staging"]["APP_NAME"] == "envoy"
    assert data["staging"]["DEBUG"] == "true"


def test_pull_writes_env_file(env_file, vault_file, tmp_path):
    push_env(env_file, vault_file, PASSWORD, "dev")
    out = tmp_path / ".env.out"
    pull_env(out, vault_file, PASSWORD, "dev", backup=False)
    content = out.read_text()
    assert "APP_NAME=envoy" in content


def test_pull_missing_profile_raises(env_file, vault_file):
    push_env(env_file, vault_file, PASSWORD, "dev")
    with pytest.raises(KeyError, match="nope"):
        pull_env(env_file, vault_file, PASSWORD, "nope", backup=False)


def test_pull_merge(tmp_path, vault_file):
    base = tmp_path / ".env"
    base.write_text("APP_NAME=envoy\nDEBUG=true\n")
    push_env(base, vault_file, PASSWORD, "prod")

    local = tmp_path / ".env.local"
    local.write_text("LOCAL_ONLY=yes\nDEBUG=false\n")

    pull_env(local, vault_file, PASSWORD, "prod", merge=True, backup=False)
    content = local.read_text()
    assert "LOCAL_ONLY=yes" in content
    assert "APP_NAME=envoy" in content


def test_list_profiles_empty_vault(tmp_path):
    vault = tmp_path / "missing.vault"
    assert list_profiles(vault, PASSWORD) == []


def test_delete_profile(env_file, vault_file):
    push_env(env_file, vault_file, PASSWORD, "to-delete")
    delete_profile(vault_file, PASSWORD, "to-delete")
    assert "to-delete" not in list_profiles(vault_file, PASSWORD)


def test_delete_missing_profile_raises(env_file, vault_file):
    push_env(env_file, vault_file, PASSWORD, "keep")
    with pytest.raises(KeyError):
        delete_profile(vault_file, PASSWORD, "ghost")


def test_push_multiple_profiles(env_file, vault_file, tmp_path):
    push_env(env_file, vault_file, PASSWORD, "dev")
    f2 = tmp_path / ".env2"
    f2.write_text("KEY=value\n")
    push_env(f2, vault_file, PASSWORD, "prod")
    profiles = list_profiles(vault_file, PASSWORD)
    assert set(profiles) == {"dev", "prod"}
