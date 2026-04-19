"""Snapshot: save and restore point-in-time copies of a vault profile."""
from __future__ import annotations

import datetime
from typing import Optional

from envoy_cli.vault import _vault_path, load_vault, save_vault

_SNAPSHOT_KEY = "__snapshots__"


def _now() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def list_snapshots(vault_file: str, password: str, profile: str) -> list[str]:
    """Return snapshot labels for *profile*, newest first."""
    data = load_vault(vault_file, password)
    snapshots: dict = data.get(_SNAPSHOT_KEY, {}).get(profile, {})
    return sorted(snapshots.keys(), reverse=True)


def create_snapshot(
    vault_file: str,
    password: str,
    profile: str,
    label: Optional[str] = None,
) -> str:
    """Save a snapshot of *profile* and return its label."""
    data = load_vault(vault_file, password)
    if profile not in data:
        raise KeyError(f"Profile '{profile}' not found in vault.")
    label = label or _now()
    snapshots = data.setdefault(_SNAPSHOT_KEY, {}).setdefault(profile, {})
    snapshots[label] = dict(data[profile])
    save_vault(vault_file, password, data)
    return label


def restore_snapshot(
    vault_file: str,
    password: str,
    profile: str,
    label: str,
) -> dict:
    """Overwrite *profile* with the snapshot identified by *label*."""
    data = load_vault(vault_file, password)
    try:
        snapshot = data[_SNAPSHOT_KEY][profile][label]
    except KeyError:
        raise KeyError(f"Snapshot '{label}' not found for profile '{profile}'.")
    data[profile] = dict(snapshot)
    save_vault(vault_file, password, data)
    return dict(snapshot)


def delete_snapshot(
    vault_file: str,
    password: str,
    profile: str,
    label: str,
) -> None:
    """Remove a snapshot permanently."""
    data = load_vault(vault_file, password)
    try:
        del data[_SNAPSHOT_KEY][profile][label]
    except KeyError:
        raise KeyError(f"Snapshot '{label}' not found for profile '{profile}'.")
    save_vault(vault_file, password, data)
