"""Scope management: restrict keys to specific environments/profiles."""

from __future__ import annotations

from typing import Dict, List

from envoy_cli.vault import load_vault, save_vault


class ScopeError(Exception):
    pass


def _scopes_store(vault: dict) -> dict:
    return vault.setdefault("__scopes__", {})


def get_scopes(vault_path: str, password: str, profile: str) -> Dict[str, List[str]]:
    """Return {key: [allowed_profile, ...]} for the given profile."""
    vault = load_vault(vault_path, password)
    store = _scopes_store(vault)
    return store.get(profile, {})


def set_scope(vault_path: str, password: str, profile: str, key: str, allowed: List[str]) -> List[str]:
    """Set the list of profiles that are allowed to read *key* in *profile*."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise ScopeError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise ScopeError(f"Key '{key}' not found in profile '{profile}'.")
    store = _scopes_store(vault)
    profile_scopes = store.setdefault(profile, {})
    profile_scopes[key] = sorted(set(allowed))
    save_vault(vault_path, password, vault)
    return profile_scopes[key]


def remove_scope(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove scope restriction for *key* in *profile*. Returns True if removed."""
    vault = load_vault(vault_path, password)
    store = _scopes_store(vault)
    profile_scopes = store.get(profile, {})
    if key not in profile_scopes:
        return False
    del profile_scopes[key]
    save_vault(vault_path, password, vault)
    return True


def is_allowed(vault_path: str, password: str, src_profile: str, key: str, target_profile: str) -> bool:
    """Return True if *target_profile* is allowed to access *key* from *src_profile*."""
    vault = load_vault(vault_path, password)
    store = _scopes_store(vault)
    key_scopes = store.get(src_profile, {}).get(key)
    if key_scopes is None:
        return True  # no restriction means open access
    return target_profile in key_scopes


def list_restricted_keys(vault_path: str, password: str, profile: str) -> List[str]:
    """Return keys in *profile* that have scope restrictions."""
    vault = load_vault(vault_path, password)
    store = _scopes_store(vault)
    return sorted(store.get(profile, {}).keys())
