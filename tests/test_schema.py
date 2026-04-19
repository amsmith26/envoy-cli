"""Tests for envoy_cli.schema."""
import json
import pytest
from pathlib import Path
from envoy_cli.schema import validate_env, load_schema, validate_or_raise, SchemaValidationError


SCHEMA = {
    "fields": {
        "APP_ENV": {"required": True, "allowed_values": ["development", "production", "test"]},
        "SECRET_KEY": {"required": True, "min_length": 8},
        "PORT": {"pattern": r"\d+"},
        "OPTIONAL_KEY": {"required": False},
    }
}


def test_valid_env_no_errors():
    env = {"APP_ENV": "production", "SECRET_KEY": "supersecret", "PORT": "8080"}
    errors = validate_env(env, SCHEMA)
    assert errors == []


def test_missing_required_key():
    env = {"APP_ENV": "production"}
    errors = validate_env(env, SCHEMA)
    assert any("SECRET_KEY" in e for e in errors)


def test_empty_required_value():
    env = {"APP_ENV": "production", "SECRET_KEY": ""}
    errors = validate_env(env, SCHEMA)
    assert any("SECRET_KEY" in e for e in errors)


def test_invalid_allowed_value():
    env = {"APP_ENV": "staging", "SECRET_KEY": "abc12345"}
    errors = validate_env(env, SCHEMA)
    assert any("APP_ENV" in e and "allowed" in e for e in errors)


def test_pattern_mismatch():
    env = {"APP_ENV": "test", "SECRET_KEY": "abc12345", "PORT": "not-a-port"}
    errors = validate_env(env, SCHEMA)
    assert any("PORT" in e and "pattern" in e for e in errors)


def test_min_length_violation():
    env = {"APP_ENV": "test", "SECRET_KEY": "short"}
    errors = validate_env(env, SCHEMA)
    assert any("SECRET_KEY" in e and "short" in e for e in errors)


def test_optional_key_missing_no_error():
    env = {"APP_ENV": "test", "SECRET_KEY": "longenough"}
    errors = validate_env(env, SCHEMA)
    assert not any("OPTIONAL_KEY" in e for e in errors)


def test_validate_or_raise_passes():
    env = {"APP_ENV": "test", "SECRET_KEY": "longenough"}
    validate_or_raise(env, SCHEMA)  # should not raise


def test_validate_or_raise_raises():
    env = {"APP_ENV": "bad"}
    with pytest.raises(SchemaValidationError) as exc_info:
        validate_or_raise(env, SCHEMA)
    assert exc_info.value.errors


def test_load_schema(tmp_path: Path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA))
    loaded = load_schema(schema_file)
    assert loaded == SCHEMA


def test_load_schema_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_schema(tmp_path / "nonexistent.json")
