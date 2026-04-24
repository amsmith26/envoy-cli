"""Tests for envoy_cli.env_transform."""

import pytest
from envoy_cli.vault import save_vault
from envoy_cli.env_transform import (
    TransformError,
    apply_transform,
    list_transforms,
    transform_key,
    transform_profile,
)


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "dev": {"APP_NAME": "hello", "SECRET": "world", "URL": "foo bar"},
        "prod": {"APP_NAME": "HELLO"},
    }
    save_vault(path, "pass", data)
    return path


def test_list_transforms_returns_sorted():
    names = list_transforms()
    assert names == sorted(names)
    assert "upper" in names
    assert "lower" in names


def test_apply_transform_upper():
    assert apply_transform("hello", "upper") == "HELLO"


def test_apply_transform_lower():
    assert apply_transform("HELLO", "lower") == "hello"


def test_apply_transform_strip():
    assert apply_transform("  hi  ", "strip") == "hi"


def test_apply_transform_reverse():
    assert apply_transform("abc", "reverse") == "cba"


def test_apply_transform_base64_roundtrip():
    encoded = apply_transform("secret", "base64encode")
    decoded = apply_transform(encoded, "base64decode")
    assert decoded == "secret"


def test_apply_transform_urlencode():
    result = apply_transform("foo bar", "urlencode")
    assert result == "foo%20bar"


def test_apply_transform_unknown_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transform("value", "nonexistent")


def test_transform_key_success(vault_file):
    old, new = transform_key(vault_file, "pass", "dev", "APP_NAME", "upper")
    assert old == "hello"
    assert new == "HELLO"


def test_transform_key_persisted(vault_file):
    transform_key(vault_file, "pass", "dev", "APP_NAME", "upper")
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "pass")
    assert vault["dev"]["APP_NAME"] == "HELLO"


def test_transform_key_dry_run_not_saved(vault_file):
    transform_key(vault_file, "pass", "dev", "APP_NAME", "upper", dry_run=True)
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "pass")
    assert vault["dev"]["APP_NAME"] == "hello"


def test_transform_key_missing_profile_raises(vault_file):
    with pytest.raises(TransformError, match="Profile 'ghost' not found"):
        transform_key(vault_file, "pass", "ghost", "KEY", "upper")


def test_transform_key_missing_key_raises(vault_file):
    with pytest.raises(TransformError, match="Key 'MISSING'"):
        transform_key(vault_file, "pass", "dev", "MISSING", "upper")


def test_transform_profile_all_keys(vault_file):
    results = transform_profile(vault_file, "pass", "dev", "upper")
    assert results["APP_NAME"] == ("hello", "HELLO")
    assert results["SECRET"] == ("world", "WORLD")


def test_transform_profile_selected_keys(vault_file):
    results = transform_profile(vault_file, "pass", "dev", "upper", keys=["APP_NAME"])
    assert "APP_NAME" in results
    assert "SECRET" not in results


def test_transform_profile_dry_run(vault_file):
    transform_profile(vault_file, "pass", "dev", "upper", dry_run=True)
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, "pass")
    assert vault["dev"]["APP_NAME"] == "hello"
