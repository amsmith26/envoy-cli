import pytest
from pathlib import Path
from envoy_cli.vault import save_vault
from envoy_cli.clone import clone_profile, list_clone_sources, CloneError

PASSWORD = "test-password"


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    data = {
        "production": {"DB_HOST": "prod-db", "DEBUG": "false"},
        "staging": {"DB_HOST": "staging-db", "DEBUG": "true"},
    }
    save_vault(str(path), PASSWORD, data)
    return str(path)


def test_clone_creates_new_profile(vault_file):
    cloned = clone_profile(vault_file, PASSWORD, "production", "production-copy")
    assert cloned["DB_HOST"] == "prod-db"


def test_clone_values_match_source(vault_file):
    clone_profile(vault_file, PASSWORD, "staging", "staging-copy")
    sources = list_clone_sources(vault_file, PASSWORD)
    assert "staging-copy" in sources


def test_clone_with_overrides(vault_file):
    cloned = clone_profile(
        vault_file, PASSWORD, "production", "prod-override",
        overrides={"DEBUG": "true", "NEW_KEY": "hello"}
    )
    assert cloned["DEBUG"] == "true"
    assert cloned["NEW_KEY"] == "hello"
    assert cloned["DB_HOST"] == "prod-db"


def test_clone_override_does_not_affect_source(vault_file):
    clone_profile(vault_file, PASSWORD, "production", "prod2", overrides={"DB_HOST": "other"})
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, PASSWORD)
    assert vault["production"]["DB_HOST"] == "prod-db"


def test_clone_missing_source_raises(vault_file):
    with pytest.raises(CloneError, match="does not exist"):
        clone_profile(vault_file, PASSWORD, "nonexistent", "copy")


def test_clone_dest_already_exists_raises(vault_file):
    with pytest.raises(CloneError, match="already exists"):
        clone_profile(vault_file, PASSWORD, "production", "staging")


def test_list_clone_sources(vault_file):
    sources = list_clone_sources(vault_file, PASSWORD)
    assert sources == ["production", "staging"]


def test_list_clone_sources_after_clone(vault_file):
    clone_profile(vault_file, PASSWORD, "production", "new-env")
    sources = list_clone_sources(vault_file, PASSWORD)
    assert "new-env" in sources
    assert len(sources) == 3
