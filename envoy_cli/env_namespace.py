"""Namespace support for grouping profiles under logical namespaces."""

from __future__ import annotations

from typing import Dict, List, Optional

from envoy_cli.vault import load_vault, save_vault


class NamespaceError(Exception):
    pass


def _ns_store(vault: dict) -> dict:
    return vault.setdefault("__namespaces__", {})


def list_namespaces(vault_path: str, password: str) -> List[str]:
    """Return sorted list of all defined namespaces."""
    vault = load_vault(vault_path, password)
    return sorted(_ns_store(vault).keys())


def set_namespace(vault_path: str, password: str, profile: str, namespace: str) -> str:
    """Assign a profile to a namespace. Returns the namespace name."""
    namespace = namespace.strip()
    if not namespace:
        raise NamespaceError("Namespace name cannot be empty.")
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise NamespaceError(f"Profile '{profile}' not found.")
    _ns_store(vault)[profile] = namespace
    save_vault(vault_path, password, vault)
    return namespace


def get_namespace(vault_path: str, password: str, profile: str) -> Optional[str]:
    """Return the namespace assigned to a profile, or None."""
    vault = load_vault(vault_path, password)
    return _ns_store(vault).get(profile)


def remove_namespace(vault_path: str, password: str, profile: str) -> bool:
    """Remove the namespace assignment for a profile. Returns True if removed."""
    vault = load_vault(vault_path, password)
    store = _ns_store(vault)
    if profile not in store:
        return False
    del store[profile]
    save_vault(vault_path, password, vault)
    return True


def get_profiles_in_namespace(vault_path: str, password: str, namespace: str) -> List[str]:
    """Return sorted list of profiles assigned to a given namespace."""
    vault = load_vault(vault_path, password)
    store = _ns_store(vault)
    return sorted(p for p, ns in store.items() if ns == namespace)
