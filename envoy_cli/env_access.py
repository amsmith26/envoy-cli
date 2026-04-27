"""Access control for profiles: restrict which users/roles may read or write a profile."""

from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class AccessError(Exception):
    pass


def _access_store(vault: dict) -> dict:
    return vault.setdefault("_access", {})


def get_access(vault_path: str, password: str, profile: str) -> dict:
    """Return the access record for a profile: {readers: [...], writers: [...]}."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise AccessError(f"Profile '{profile}' not found.")
    store = _access_store(vault)
    return store.get(profile, {"readers": [], "writers": []})


def grant_access(vault_path: str, password: str, profile: str, principal: str, role: str) -> dict:
    """Grant *principal* the given *role* ('read' or 'write') on *profile*."""
    if role not in ("read", "write"):
        raise AccessError(f"Invalid role '{role}'. Must be 'read' or 'write'.")
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise AccessError(f"Profile '{profile}' not found.")
    store = _access_store(vault)
    record = store.setdefault(profile, {"readers": [], "writers": []})
    key = "readers" if role == "read" else "writers"
    if principal not in record[key]:
        record[key].append(principal)
        record[key].sort()
    save_vault(vault_path, password, vault)
    return record


def revoke_access(vault_path: str, password: str, profile: str, principal: str, role: str) -> dict:
    """Revoke *principal*'s *role* on *profile*."""
    if role not in ("read", "write"):
        raise AccessError(f"Invalid role '{role}'. Must be 'read' or 'write'.")
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise AccessError(f"Profile '{profile}' not found.")
    store = _access_store(vault)
    record = store.get(profile, {"readers": [], "writers": []})
    key = "readers" if role == "read" else "writers"
    record[key] = [p for p in record.get(key, []) if p != principal]
    store[profile] = record
    save_vault(vault_path, password, vault)
    return record


def check_access(vault_path: str, password: str, profile: str, principal: str, role: str) -> bool:
    """Return True if *principal* has *role* on *profile*."""
    if role not in ("read", "write"):
        raise AccessError(f"Invalid role '{role}'. Must be 'read' or 'write'.")
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise AccessError(f"Profile '{profile}' not found.")
    store = _access_store(vault)
    record = store.get(profile, {"readers": [], "writers": []})
    key = "readers" if role == "read" else "writers"
    return principal in record.get(key, [])
