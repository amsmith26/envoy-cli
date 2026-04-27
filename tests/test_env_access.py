"""Tests for envoy_cli.env_access."""

import pytest

from envoy_cli.env_access import AccessError, check_access, get_access, grant_access, revoke_access
from envoy_cli.vault import save_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, "secret", {"production": {"DB_URL": "postgres://localhost/prod"}, "staging": {"DB_URL": "postgres://localhost/staging"}})
    return path


def test_get_access_empty(vault_file):
    record = get_access(vault_file, "secret", "production")
    assert record == {"readers": [], "writers": []}


def test_grant_read_access(vault_file):
    record = grant_access(vault_file, "secret", "production", "alice", "read")
    assert "alice" in record["readers"]
    assert "alice" not in record["writers"]


def test_grant_write_access(vault_file):
    record = grant_access(vault_file, "secret", "production", "bob", "write")
    assert "bob" in record["writers"]
    assert "bob" not in record["readers"]


def test_grant_persisted(vault_file):
    grant_access(vault_file, "secret", "production", "alice", "read")
    record = get_access(vault_file, "secret", "production")
    assert "alice" in record["readers"]


def test_grant_duplicate_no_duplicates(vault_file):
    grant_access(vault_file, "secret", "production", "alice", "read")
    grant_access(vault_file, "secret", "production", "alice", "read")
    record = get_access(vault_file, "secret", "production")
    assert record["readers"].count("alice") == 1


def test_grant_readers_sorted(vault_file):
    grant_access(vault_file, "secret", "production", "charlie", "read")
    grant_access(vault_file, "secret", "production", "alice", "read")
    record = get_access(vault_file, "secret", "production")
    assert record["readers"] == sorted(record["readers"])


def test_revoke_access(vault_file):
    grant_access(vault_file, "secret", "production", "alice", "read")
    record = revoke_access(vault_file, "secret", "production", "alice", "read")
    assert "alice" not in record["readers"]


def test_revoke_nonexistent_principal_is_noop(vault_file):
    record = revoke_access(vault_file, "secret", "production", "nobody", "write")
    assert "nobody" not in record["writers"]


def test_check_access_true(vault_file):
    grant_access(vault_file, "secret", "staging", "dev", "write")
    assert check_access(vault_file, "secret", "staging", "dev", "write") is True


def test_check_access_false(vault_file):
    assert check_access(vault_file, "secret", "staging", "unknown", "read") is False


def test_grant_unknown_profile_raises(vault_file):
    with pytest.raises(AccessError, match="not found"):
        grant_access(vault_file, "secret", "ghost", "alice", "read")


def test_get_access_unknown_profile_raises(vault_file):
    with pytest.raises(AccessError, match="not found"):
        get_access(vault_file, "secret", "ghost")


def test_grant_invalid_role_raises(vault_file):
    with pytest.raises(AccessError, match="Invalid role"):
        grant_access(vault_file, "secret", "production", "alice", "admin")
