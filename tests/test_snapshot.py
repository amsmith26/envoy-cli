"""Tests for envoy_cli.snapshot."""
import pytest

from envoy_cli.snapshot import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)
from envoy_cli.vault import save_vault

PASSWORD = "s3cr3t"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, PASSWORD, {"prod": {"KEY": "value1", "OTHER": "abc"}})
    return path


def test_create_snapshot_returns_label(vault_file):
    label = create_snapshot(vault_file, PASSWORD, "prod")
    assert isinstance(label, str)
    assert len(label) > 0


def test_list_snapshots_empty(vault_file):
    assert list_snapshots(vault_file, PASSWORD, "prod") == []


def test_list_snapshots_after_create(vault_file):
    label = create_snapshot(vault_file, PASSWORD, "prod", label="snap1")
    labels = list_snapshots(vault_file, PASSWORD, "prod")
    assert label in labels


def test_multiple_snapshots_newest_first(vault_file):
    create_snapshot(vault_file, PASSWORD, "prod", label="snap_a")
    create_snapshot(vault_file, PASSWORD, "prod", label="snap_b")
    labels = list_snapshots(vault_file, PASSWORD, "prod")
    assert labels == sorted(labels, reverse=True)


def test_restore_snapshot_overwrites_profile(vault_file):
    create_snapshot(vault_file, PASSWORD, "prod", label="before")
    # Mutate the profile
    from envoy_cli.vault import load_vault
    data = load_vault(vault_file, PASSWORD)
    data["prod"]["KEY"] = "changed"
    save_vault(vault_file, PASSWORD, data)
    # Restore
    restored = restore_snapshot(vault_file, PASSWORD, "prod", "before")
    assert restored["KEY"] == "value1"
    data2 = load_vault(vault_file, PASSWORD)
    assert data2["prod"]["KEY"] == "value1"


def test_restore_missing_snapshot_raises(vault_file):
    with pytest.raises(KeyError, match="ghost"):
        restore_snapshot(vault_file, PASSWORD, "prod", "ghost")


def test_delete_snapshot(vault_file):
    create_snapshot(vault_file, PASSWORD, "prod", label="to_delete")
    delete_snapshot(vault_file, PASSWORD, "prod", "to_delete")
    assert "to_delete" not in list_snapshots(vault_file, PASSWORD, "prod")


def test_delete_missing_snapshot_raises(vault_file):
    with pytest.raises(KeyError):
        delete_snapshot(vault_file, PASSWORD, "prod", "nope")


def test_create_snapshot_missing_profile_raises(vault_file):
    with pytest.raises(KeyError, match="staging"):
        create_snapshot(vault_file, PASSWORD, "staging")
