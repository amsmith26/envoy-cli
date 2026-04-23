"""Tests for envoy_cli.env_validate."""

import pytest

from envoy_cli.env_validate import (
    ValidationRuleError,
    get_rules,
    remove_rule,
    set_rule,
    validate_profile,
)
from envoy_cli.vault import save_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, "secret", {"profiles": {"prod": {"PORT": "8080", "EMAIL": "admin@example.com", "RATIO": "0.5"}}})
    return path


def test_set_rule_and_get_rules(vault_file):
    set_rule(vault_file, "secret", "prod", "PORT", {"type": "int"})
    rules = get_rules(vault_file, "secret", "prod")
    assert "PORT" in rules
    assert rules["PORT"]["type"] == "int"


def test_set_rule_unknown_profile_raises(vault_file):
    with pytest.raises(ValidationRuleError, match="Profile 'staging' not found"):
        set_rule(vault_file, "secret", "staging", "PORT", {"type": "int"})


def test_set_rule_unknown_key_raises(vault_file):
    with pytest.raises(ValidationRuleError, match="Key 'MISSING' not found"):
        set_rule(vault_file, "secret", "prod", "MISSING", {"type": "str"})


def test_set_rule_invalid_type_raises(vault_file):
    with pytest.raises(ValidationRuleError, match="Unsupported type"):
        set_rule(vault_file, "secret", "prod", "PORT", {"type": "uuid"})


def test_remove_rule_existing(vault_file):
    set_rule(vault_file, "secret", "prod", "PORT", {"type": "int"})
    removed = remove_rule(vault_file, "secret", "prod", "PORT")
    assert removed is True
    assert get_rules(vault_file, "secret", "prod") == {}


def test_remove_rule_nonexistent_returns_false(vault_file):
    removed = remove_rule(vault_file, "secret", "prod", "PORT")
    assert removed is False


def test_validate_profile_passes(vault_file):
    set_rule(vault_file, "secret", "prod", "PORT", {"type": "int"})
    violations = validate_profile(vault_file, "secret", "prod")
    assert violations == []


def test_validate_profile_int_fails(vault_file):
    from envoy_cli.vault import load_vault, save_vault as sv
    vault = load_vault(vault_file, "secret")
    vault["profiles"]["prod"]["PORT"] = "not_a_number"
    sv(vault_file, "secret", vault)
    set_rule(vault_file, "secret", "prod", "PORT", {"type": "int"})
    violations = validate_profile(vault_file, "secret", "prod")
    assert len(violations) == 1
    assert violations[0].key == "PORT"


def test_validate_profile_email_passes(vault_file):
    set_rule(vault_file, "secret", "prod", "EMAIL", {"type": "email"})
    violations = validate_profile(vault_file, "secret", "prod")
    assert violations == []


def test_validate_profile_min_length_fails(vault_file):
    set_rule(vault_file, "secret", "prod", "PORT", {"min_length": 10})
    violations = validate_profile(vault_file, "secret", "prod")
    assert any(v.key == "PORT" for v in violations)


def test_validate_profile_max_length_fails(vault_file):
    set_rule(vault_file, "secret", "prod", "PORT", {"max_length": 2})
    violations = validate_profile(vault_file, "secret", "prod")
    assert any("too long" in v.message for v in violations)


def test_validate_profile_float(vault_file):
    set_rule(vault_file, "secret", "prod", "RATIO", {"type": "float"})
    violations = validate_profile(vault_file, "secret", "prod")
    assert violations == []


def test_get_rules_empty_profile(vault_file):
    rules = get_rules(vault_file, "secret", "prod")
    assert rules == {}
