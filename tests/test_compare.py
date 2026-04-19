import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.compare import compare_profiles, compare_env_to_profile, summary

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "production": {"DB_HOST": "prod-db", "API_KEY": "abc123", "TIMEOUT": "30"},
        "staging": {"DB_HOST": "staging-db", "API_KEY": "abc123", "DEBUG": "true"},
    }
    save_vault(str(path), PASSWORD, vault)
    return str(path)


def test_compare_profiles_changed_key(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    changed = [e for e in result if e["key"] == "DB_HOST"]
    assert len(changed) == 1
    assert changed[0]["change"] == "changed"
    assert changed[0]["value_a"] == "prod-db"
    assert changed[0]["value_b"] == "staging-db"


def test_compare_profiles_unchanged_key(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    unchanged = [e for e in result if e["key"] == "API_KEY"]
    assert unchanged[0]["change"] == "unchanged"


def test_compare_profiles_removed_key(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    removed = [e for e in result if e["key"] == "TIMEOUT"]
    assert removed[0]["change"] == "removed"
    assert removed[0]["value_b"] is None


def test_compare_profiles_added_key(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    added = [e for e in result if e["key"] == "DEBUG"]
    assert added[0]["change"] == "added"
    assert added[0]["value_a"] is None


def test_compare_profiles_missing_profile_raises(vault_file):
    with pytest.raises(KeyError, match="missing"):
        compare_profiles(vault_file, PASSWORD, "production", "missing")


def test_compare_env_to_profile(vault_file):
    local_env = {"DB_HOST": "local-db", "API_KEY": "abc123", "NEW_KEY": "val"}
    result = compare_env_to_profile(local_env, vault_file, PASSWORD, "production")

    keys = {e["key"]: e["change"] for e in result}
    assert keys["DB_HOST"] == "changed"
    assert keys["API_KEY"] == "unchanged"
    assert keys["NEW_KEY"] == "removed"  # in local but not in profile_b (production)
    assert keys["TIMEOUT"] == "added"   # in production but not in local


def test_summary_counts(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    added, removed, changed, unchanged = summary(result)
    assert added == 1    # DEBUG
    assert removed == 1  # TIMEOUT
    assert changed == 1  # DB_HOST
    assert unchanged == 1  # API_KEY


def test_all_keys_sorted(vault_file):
    result = compare_profiles(vault_file, PASSWORD, "production", "staging")
    keys = [e["key"] for e in result]
    assert keys == sorted(keys)
