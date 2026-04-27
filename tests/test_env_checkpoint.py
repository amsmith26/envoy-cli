"""Tests for envoy_cli.env_checkpoint."""
import pytest

from envoy_cli.env_checkpoint import (
    CheckpointError,
    create_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)
from envoy_cli.vault import save_vault


PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    initial = {
        "dev": {"APP_ENV": "development", "DEBUG": "true"},
        "prod": {"APP_ENV": "production", "DEBUG": "false"},
    }
    save_vault(path, PASSWORD, initial)
    return path


def test_create_checkpoint_returns_label(vault_file):
    label = create_checkpoint(vault_file, PASSWORD, "dev", label="v1")
    assert label == "v1"


def test_create_checkpoint_auto_label(vault_file):
    label = create_checkpoint(vault_file, PASSWORD, "dev")
    assert "checkpoint-" in label


def test_list_checkpoints_empty(vault_file):
    result = list_checkpoints(vault_file, PASSWORD, "dev")
    assert result == []


def test_list_checkpoints_after_create(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="snap1")
    result = list_checkpoints(vault_file, PASSWORD, "dev")
    assert len(result) == 1
    assert result[0]["label"] == "snap1"


def test_multiple_checkpoints_newest_first(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="first")
    create_checkpoint(vault_file, PASSWORD, "dev", label="second")
    labels = [e["label"] for e in list_checkpoints(vault_file, PASSWORD, "dev")]
    assert labels[0] == "second"
    assert labels[1] == "first"


def test_create_duplicate_label_raises(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="dup")
    with pytest.raises(CheckpointError, match="already exists"):
        create_checkpoint(vault_file, PASSWORD, "dev", label="dup")


def test_create_checkpoint_unknown_profile_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        create_checkpoint(vault_file, PASSWORD, "staging", label="x")


def test_restore_checkpoint_reverts_env(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="before-change")
    # Mutate vault externally
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, PASSWORD)
    vault["dev"]["DEBUG"] = "false"
    save_vault(vault_file, PASSWORD, vault)
    # Restore
    env = restore_checkpoint(vault_file, PASSWORD, "dev", "before-change")
    assert env["DEBUG"] == "true"


def test_restore_checkpoint_missing_label_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        restore_checkpoint(vault_file, PASSWORD, "dev", "ghost")


def test_delete_checkpoint_removes_entry(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="to-delete")
    remaining = delete_checkpoint(vault_file, PASSWORD, "dev", "to-delete")
    assert "to-delete" not in remaining


def test_delete_missing_checkpoint_raises(vault_file):
    with pytest.raises(CheckpointError, match="not found"):
        delete_checkpoint(vault_file, PASSWORD, "dev", "no-such")


def test_checkpoint_stores_snapshot_of_values(vault_file):
    create_checkpoint(vault_file, PASSWORD, "dev", label="snap")
    entries = list_checkpoints(vault_file, PASSWORD, "dev")
    assert entries[0]["env"]["APP_ENV"] == "development"
