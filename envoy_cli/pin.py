"""Pin specific keys in a profile to prevent them from being overwritten during pulls or merges."""

from typing import List
from envoy_cli.vault import load_vault, save_vault


class PinError(Exception):
    pass


_PINS_KEY = "__pins__"


def _pins_key(profile: str) -> str:
    return f"{_PINS_KEY}:{profile}"


def get_pinned_keys(vault: dict, profile: str) -> List[str]:
    """Return the list of pinned keys for a profile."""
    return list(vault.get(_pins_key(profile), []))


def pin_key(vault_file: str, password: str, profile: str, key: str) -> List[str]:
    """Pin a key in a profile. Raises PinError if profile or key doesn't exist."""
    vault = load_vault(vault_file, password)

    if profile not in vault:
        raise PinError(f"Profile '{profile}' not found.")

    if key not in vault[profile]:
        raise PinError(f"Key '{key}' not found in profile '{profile}'.")

    pk = _pins_key(profile)
    pins = set(vault.get(pk, []))
    pins.add(key)
    vault[pk] = sorted(pins)
    save_vault(vault_file, password, vault)
    return vault[pk]


def unpin_key(vault_file: str, password: str, profile: str, key: str) -> List[str]:
    """Unpin a key in a profile. Returns updated pin list."""
    vault = load_vault(vault_file, password)

    pk = _pins_key(profile)
    pins = set(vault.get(pk, []))
    pins.discard(key)
    vault[pk] = sorted(pins)
    save_vault(vault_file, password, vault)
    return vault[pk]


def is_pinned(vault: dict, profile: str, key: str) -> bool:
    """Return True if the key is pinned in the given profile."""
    return key in vault.get(_pins_key(profile), [])


def apply_pins(base: dict, incoming: dict, pinned_keys: List[str]) -> dict:
    """Merge incoming into base, but preserve pinned keys from base."""
    merged = {**incoming}
    for key in pinned_keys:
        if key in base:
            merged[key] = base[key]
    return merged
