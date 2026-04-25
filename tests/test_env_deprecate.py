"""Tests for envoy_cli.env_deprecate."""

import pytest

from envoy_cli.env_deprecate import (
    DeprecateError,
    check_deprecated_usage,
    deprecate_key,
    get_deprecations,
    is_deprecated,
    undeprecate_key,
)
from envoy_cli.vault import save_vault


PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "vault.env.vault"
    vault = {
        "profiles": {
            "dev": {"OLD_API_KEY": "abc123", "NEW_API_KEY": "xyz789", "PORT": "8080"}
        }
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_deprecate_key_returns_record(vault_file):
    record = deprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY", reason="Use NEW_API_KEY", replacement="NEW_API_KEY")
    assert record["reason"] == "Use NEW_API_KEY"
    assert record["replacement"] == "NEW_API_KEY"


def test_deprecate_key_persisted(vault_file):
    deprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY", reason="legacy")
    deps = get_deprecations(vault_file, PASSWORD, "dev")
    assert "OLD_API_KEY" in deps
    assert deps["OLD_API_KEY"]["reason"] == "legacy"


def test_deprecate_unknown_profile_raises(vault_file):
    with pytest.raises(DeprecateError, match="Profile"):
        deprecate_key(vault_file, PASSWORD, "prod", "OLD_API_KEY")


def test_deprecate_unknown_key_raises(vault_file):
    with pytest.raises(DeprecateError, match="Key"):
        deprecate_key(vault_file, PASSWORD, "dev", "NONEXISTENT")


def test_is_deprecated_true(vault_file):
    deprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY")
    assert is_deprecated(vault_file, PASSWORD, "dev", "OLD_API_KEY") is True


def test_is_deprecated_false(vault_file):
    assert is_deprecated(vault_file, PASSWORD, "dev", "PORT") is False


def test_undeprecate_key_removes_entry(vault_file):
    deprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY")
    result = undeprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY")
    assert result is True
    assert is_deprecated(vault_file, PASSWORD, "dev", "OLD_API_KEY") is False


def test_undeprecate_key_not_found_returns_false(vault_file):
    result = undeprecate_key(vault_file, PASSWORD, "dev", "PORT")
    assert result is False


def test_get_deprecations_empty(vault_file):
    deps = get_deprecations(vault_file, PASSWORD, "dev")
    assert deps == {}


def test_check_deprecated_usage_finds_violations(vault_file):
    deprecate_key(vault_file, PASSWORD, "dev", "OLD_API_KEY", reason="Use NEW_API_KEY", replacement="NEW_API_KEY")
    violations = check_deprecated_usage(vault_file, PASSWORD, "dev")
    assert len(violations) == 1
    assert violations[0]["key"] == "OLD_API_KEY"
    assert violations[0]["replacement"] == "NEW_API_KEY"


def test_check_deprecated_usage_no_violations(vault_file):
    violations = check_deprecated_usage(vault_file, PASSWORD, "dev")
    assert violations == []


def test_deprecate_key_no_replacement(vault_file):
    record = deprecate_key(vault_file, PASSWORD, "dev", "PORT", reason="unused")
    assert record["replacement"] is None
