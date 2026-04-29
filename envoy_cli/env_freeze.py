"""Freeze/unfreeze profiles to prevent accidental modifications."""
from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class FreezeError(Exception):
    pass


def _freeze_store(vault: dict) -> dict:
    return vault.setdefault("__freeze__", {})


def get_frozen_profiles(vault_path: str, password: str) -> List[str]:
    """Return sorted list of frozen profile names."""
    vault = load_vault(vault_path, password)
    store = _freeze_store(vault)
    return sorted(store.get("profiles", []))


def freeze_profile(vault_path: str, password: str, profile: str) -> List[str]:
    """Mark a profile as frozen. Raises FreezeError if profile does not exist."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise FreezeError(f"Profile '{profile}' not found.")
    store = _freeze_store(vault)
    frozen = set(store.get("profiles", []))
    frozen.add(profile)
    store["profiles"] = sorted(frozen)
    save_vault(vault_path, password, vault)
    return store["profiles"]


def unfreeze_profile(vault_path: str, password: str, profile: str) -> List[str]:
    """Remove freeze from a profile. Raises FreezeError if not frozen."""
    vault = load_vault(vault_path, password)
    store = _freeze_store(vault)
    frozen = set(store.get("profiles", []))
    if profile not in frozen:
        raise FreezeError(f"Profile '{profile}' is not frozen.")
    frozen.discard(profile)
    store["profiles"] = sorted(frozen)
    save_vault(vault_path, password, vault)
    return store["profiles"]


def is_frozen(vault_path: str, password: str, profile: str) -> bool:
    """Return True if the given profile is frozen."""
    return profile in get_frozen_profiles(vault_path, password)


def assert_not_frozen(vault_path: str, password: str, profile: str) -> None:
    """Raise FreezeError if the profile is frozen."""
    if is_frozen(vault_path, password, profile):
        raise FreezeError(
            f"Profile '{profile}' is frozen and cannot be modified. "
            "Use 'envoy freeze unfreeze' to unlock it."
        )
