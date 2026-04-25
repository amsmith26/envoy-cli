"""Profile inheritance: allow a profile to inherit keys from a parent profile."""

from __future__ import annotations

from typing import Optional

from envoy_cli.vault import load_vault, save_vault

_INHERIT_KEY = "__inherit__"


class InheritError(Exception):
    pass


def _inherit_store(vault: dict) -> dict:
    return vault.setdefault(_INHERIT_KEY, {})


def get_parent(vault: dict, profile: str) -> Optional[str]:
    """Return the parent profile name for *profile*, or None."""
    return _inherit_store(vault).get(profile)


def set_parent(vault_file: str, password: str, profile: str, parent: str) -> str:
    """Set *parent* as the inheritance source for *profile*."""
    vault = load_vault(vault_file, password)
    if profile not in vault.get("profiles", {}):
        raise InheritError(f"Profile '{profile}' does not exist.")
    if parent not in vault.get("profiles", {}):
        raise InheritError(f"Parent profile '{parent}' does not exist.")
    if parent == profile:
        raise InheritError("A profile cannot inherit from itself.")
    _inherit_store(vault)[profile] = parent
    save_vault(vault_file, password, vault)
    return parent


def remove_parent(vault_file: str, password: str, profile: str) -> bool:
    """Remove the inheritance link for *profile*. Returns True if removed."""
    vault = load_vault(vault_file, password)
    store = _inherit_store(vault)
    if profile not in store:
        return False
    del store[profile]
    save_vault(vault_file, password, vault)
    return True


def resolve_inherited(vault: dict, profile: str) -> dict:
    """Return the effective env for *profile* after applying inheritance.

    Parent keys are used as defaults; child keys take precedence.
    Circular references are detected and raise InheritError.
    """
    visited: list[str] = []
    merged: dict = {}
    current = profile
    while current is not None:
        if current in visited:
            raise InheritError(f"Circular inheritance detected: {' -> '.join(visited + [current])}.")
        visited.append(current)
        profiles = vault.get("profiles", {})
        if current not in profiles:
            raise InheritError(f"Profile '{current}' does not exist.")
        # Parent keys fill in only missing keys
        for k, v in profiles[current].items():
            if k not in merged:
                merged[k] = v
        current = _inherit_store(vault).get(current)
    return merged
