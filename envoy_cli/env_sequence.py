"""Manage ordered key sequences within a profile."""
from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class SequenceError(Exception):
    pass


def _sequences_store(vault: dict) -> dict:
    return vault.setdefault("__sequences__", {})


def get_sequence(vault_path: str, password: str, profile: str, name: str) -> List[str]:
    """Return the ordered list of keys for a named sequence."""
    vault = load_vault(vault_path, password)
    store = _sequences_store(vault)
    return list(store.get(profile, {}).get(name, []))


def list_sequences(vault_path: str, password: str, profile: str) -> List[str]:
    """Return all sequence names defined for a profile."""
    vault = load_vault(vault_path, password)
    store = _sequences_store(vault)
    return sorted(store.get(profile, {}).keys())


def set_sequence(
    vault_path: str, password: str, profile: str, name: str, keys: List[str]
) -> List[str]:
    """Define or replace a named sequence of keys for a profile."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise SequenceError(f"Profile '{profile}' not found.")
    env = vault[profile]
    for key in keys:
        if key not in env:
            raise SequenceError(f"Key '{key}' not found in profile '{profile}'.")
    if len(keys) != len(set(keys)):
        raise SequenceError("Sequence contains duplicate keys.")
    store = _sequences_store(vault)
    store.setdefault(profile, {})[name] = list(keys)
    save_vault(vault_path, password, vault)
    return list(keys)


def remove_sequence(vault_path: str, password: str, profile: str, name: str) -> bool:
    """Remove a named sequence from a profile. Returns True if it existed."""
    vault = load_vault(vault_path, password)
    store = _sequences_store(vault)
    profile_sequences = store.get(profile, {})
    if name not in profile_sequences:
        return False
    del profile_sequences[name]
    save_vault(vault_path, password, vault)
    return True


def resolve_sequence(
    vault_path: str, password: str, profile: str, name: str
) -> List[dict]:
    """Return ordered list of {key, value} dicts for a named sequence."""
    vault = load_vault(vault_path, password)
    store = _sequences_store(vault)
    keys = store.get(profile, {}).get(name)
    if keys is None:
        raise SequenceError(f"Sequence '{name}' not found in profile '{profile}'.")
    env = vault.get(profile, {})
    return [{"key": k, "value": env.get(k, "")} for k in keys]
