"""TTL (time-to-live) support for environment variable keys."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from envoy_cli.vault import load_vault, save_vault


class TTLError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ttl_store(vault: dict) -> dict:
    return vault.setdefault("__ttl__", {})


def set_ttl(vault_file: str, password: str, profile: str, key: str, seconds: int) -> str:
    """Set a TTL for a key. Returns the expiry ISO timestamp."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise TTLError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise TTLError(f"Key '{key}' not found in profile '{profile}'.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    expiry = _utcnow() + timedelta(seconds=seconds)
    expiry_str = expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
    store = _ttl_store(vault)
    store.setdefault(profile, {})[key] = expiry_str
    save_vault(vault_file, password, vault)
    return expiry_str


def get_ttl(vault_file: str, password: str, profile: str, key: str) -> Optional[str]:
    """Return the expiry timestamp string for a key, or None."""
    vault = load_vault(vault_file, password)
    return _ttl_store(vault).get(profile, {}).get(key)


def remove_ttl(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Remove TTL for a key. Returns True if removed, False if not set."""
    vault = load_vault(vault_file, password)
    store = _ttl_store(vault)
    if key in store.get(profile, {}):
        del store[profile][key]
        save_vault(vault_file, password, vault)
        return True
    return False


def is_expired(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Return True if the key has a TTL that has passed."""
    expiry_str = get_ttl(vault_file, password, profile, key)
    if expiry_str is None:
        return False
    expiry = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return _utcnow() >= expiry


def list_ttls(vault_file: str, password: str, profile: str) -> dict:
    """Return a dict of key -> expiry string for all keys with a TTL."""
    vault = load_vault(vault_file, password)
    return dict(sorted(_ttl_store(vault).get(profile, {}).items()))


def purge_expired(vault_file: str, password: str, profile: str) -> list:
    """Remove all expired keys from the profile. Returns list of removed keys."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise TTLError(f"Profile '{profile}' not found.")
    store = _ttl_store(vault)
    now = _utcnow()
    removed = []
    for key, expiry_str in list(store.get(profile, {}).items()):
        expiry = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if now >= expiry:
            vault[profile].pop(key, None)
            del store[profile][key]
            removed.append(key)
    if removed:
        save_vault(vault_file, password, vault)
    return sorted(removed)
