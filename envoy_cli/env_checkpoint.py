"""Checkpoint support: save and restore named in-vault checkpoints per profile."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from envoy_cli.vault import load_vault, save_vault


class CheckpointError(Exception):
    pass


def _checkpoints_store(vault: dict) -> dict:
    return vault.setdefault("__checkpoints__", {})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def list_checkpoints(vault_file: str, password: str, profile: str) -> List[dict]:
    """Return checkpoints for *profile*, newest first."""
    vault = load_vault(vault_file, password)
    store = _checkpoints_store(vault)
    entries = store.get(profile, [])
    return sorted(entries, key=lambda e: e["created_at"], reverse=True)


def create_checkpoint(
    vault_file: str, password: str, profile: str, label: Optional[str] = None
) -> str:
    """Snapshot current profile env into a named checkpoint; return the label."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise CheckpointError(f"Profile '{profile}' not found.")
    store = _checkpoints_store(vault)
    entries: List[dict] = store.setdefault(profile, [])
    created_at = _now()
    resolved_label = label or f"checkpoint-{created_at}"
    if any(e["label"] == resolved_label for e in entries):
        raise CheckpointError(f"Checkpoint '{resolved_label}' already exists.")
    entries.append(
        {"label": resolved_label, "created_at": created_at, "env": dict(vault[profile])}
    )
    save_vault(vault_file, password, vault)
    return resolved_label


def restore_checkpoint(vault_file: str, password: str, profile: str, label: str) -> dict:
    """Restore profile env from checkpoint *label*; return restored env."""
    vault = load_vault(vault_file, password)
    store = _checkpoints_store(vault)
    entries = store.get(profile, [])
    match = next((e for e in entries if e["label"] == label), None)
    if match is None:
        raise CheckpointError(f"Checkpoint '{label}' not found for profile '{profile}'.")
    vault[profile] = dict(match["env"])
    save_vault(vault_file, password, vault)
    return dict(match["env"])


def delete_checkpoint(vault_file: str, password: str, profile: str, label: str) -> List[str]:
    """Remove checkpoint *label* from *profile*; return remaining labels."""
    vault = load_vault(vault_file, password)
    store = _checkpoints_store(vault)
    entries = store.get(profile, [])
    new_entries = [e for e in entries if e["label"] != label]
    if len(new_entries) == len(entries):
        raise CheckpointError(f"Checkpoint '{label}' not found for profile '{profile}'.")
    store[profile] = new_entries
    save_vault(vault_file, password, vault)
    return [e["label"] for e in new_entries]
