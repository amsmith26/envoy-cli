"""Mask sensitive env keys so their values are redacted in output."""

from __future__ import annotations

from typing import Dict, List

from envoy_cli.vault import load_vault, save_vault

_MASKS_KEY = "__masks__"


class MaskError(Exception):
    pass


def _masks_store(vault: dict) -> dict:
    return vault.setdefault(_MASKS_KEY, {})


def get_masked_keys(vault: dict, profile: str) -> List[str]:
    """Return sorted list of masked keys for *profile*."""
    return sorted(_masks_store(vault).get(profile, []))


def mask_key(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Mark *key* in *profile* as masked. Returns updated masked-key list."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise MaskError(f"Profile '{profile}' not found.")
    env = vault[profile]
    if key not in env:
        raise MaskError(f"Key '{key}' not found in profile '{profile}'.")
    store = _masks_store(vault)
    masked = set(store.get(profile, []))
    masked.add(key)
    store[profile] = sorted(masked)
    save_vault(vault_path, password, vault)
    return store[profile]


def unmask_key(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Remove mask from *key* in *profile*. Returns updated masked-key list."""
    vault = load_vault(vault_path, password)
    store = _masks_store(vault)
    masked = set(store.get(profile, []))
    masked.discard(key)
    store[profile] = sorted(masked)
    save_vault(vault_path, password, vault)
    return store[profile]


def apply_masks(env: Dict[str, str], masked_keys: List[str], placeholder: str = "***") -> Dict[str, str]:
    """Return a copy of *env* with masked keys replaced by *placeholder*."""
    return {k: (placeholder if k in masked_keys else v) for k, v in env.items()}
