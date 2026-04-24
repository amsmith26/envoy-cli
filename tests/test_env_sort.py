"""Tests for envoy_cli.env_sort."""

import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.env_sort import sort_profile, preview_sort, SortError

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    data = {
        "prod": {
            "ZEBRA": "z",
            "ALPHA": "a",
            "MANGO": "m",
            "BETA": "b",
        }
    }
    save_vault(str(path), PASSWORD, data)
    return str(path)


def test_sort_profile_alphabetical(vault_file):
    result = sort_profile(vault_file, PASSWORD, "prod")
    assert list(result.keys()) == ["ALPHA", "BETA", "MANGO", "ZEBRA"]


def test_sort_profile_reverse(vault_file):
    result = sort_profile(vault_file, PASSWORD, "prod", reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "BETA", "ALPHA"]


def test_sort_profile_values_preserved(vault_file):
    result = sort_profile(vault_file, PASSWORD, "prod")
    assert result["ALPHA"] == "a"
    assert result["ZEBRA"] == "z"
    assert result["MANGO"] == "m"
    assert result["BETA"] == "b"


def test_sort_profile_persisted(vault_file):
    sort_profile(vault_file, PASSWORD, "prod")
    # Re-load and verify order persisted
    result2 = sort_profile(vault_file, PASSWORD, "prod")
    assert list(result2.keys()) == ["ALPHA", "BETA", "MANGO", "ZEBRA"]


def test_sort_profile_unknown_profile_raises(vault_file):
    with pytest.raises(SortError, match="not found"):
        sort_profile(vault_file, PASSWORD, "nonexistent")


def test_sort_profile_with_key_filter(vault_file):
    result = sort_profile(vault_file, PASSWORD, "prod", keys=["ZEBRA", "ALPHA"])
    keys = list(result.keys())
    # ALPHA and ZEBRA sorted first, remainder at end
    assert keys[0] == "ALPHA"
    assert keys[1] == "ZEBRA"
    assert set(keys[2:]) == {"MANGO", "BETA"}


def test_sort_profile_unknown_key_in_filter_raises(vault_file):
    with pytest.raises(SortError, match="Keys not found"):
        sort_profile(vault_file, PASSWORD, "prod", keys=["ALPHA", "MISSING"])


def test_preview_sort_returns_sorted_keys(vault_file):
    keys = preview_sort(vault_file, PASSWORD, "prod")
    assert keys == ["ALPHA", "BETA", "MANGO", "ZEBRA"]


def test_preview_sort_does_not_modify_vault(vault_file):
    from envoy_cli.vault import load_vault
    before = list(load_vault(vault_file, PASSWORD)["prod"].keys())
    preview_sort(vault_file, PASSWORD, "prod")
    after = list(load_vault(vault_file, PASSWORD)["prod"].keys())
    assert before == after


def test_preview_sort_unknown_profile_raises(vault_file):
    with pytest.raises(SortError, match="not found"):
        preview_sort(vault_file, PASSWORD, "ghost")
