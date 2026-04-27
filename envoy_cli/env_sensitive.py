"""Mark keys as sensitive to prevent accidental exposure in logs/output."""

from __future__ import annotations

from envoy_cli.vault import load_vault, save_vault


class SensitiveError(Exception):
    pass


def _sensitive_store(vault: dict, profile: str) -> dict:
    return vault.setdefault("_sensitive", {}).setdefault(profile, {})


def get_sensitive_keys(vault_path: str, password: str, profile: str) -> list[str]:
    """Return sorted list of keys marked sensitive for a profile."""
    vault = load_vault(vault_path, password)
    store = _sensitive_store(vault, profile)
    return sorted(store.get("keys", []))


def mark_sensitive(vault_path: str, password: str, profile: str, key: str) -> list[str]:
    """Mark a key as sensitive. Raises SensitiveError if profile or key not found."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise SensitiveError(f"Profile '{profile}' not found.")
    if key not in vault["profiles"][profile]:
        raise SensitiveError(f"Key '{key}' not found in profile '{profile}'.")
    store = _sensitive_store(vault, profile)
    keys = set(store.get("keys", []))
    keys.add(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def unmark_sensitive(vault_path: str, password: str, profile: str, key: str) -> list[str]:
    """Remove sensitive marking from a key. Returns updated list."""
    vault = load_vault(vault_path, password)
    store = _sensitive_store(vault, profile)
    keys = set(store.get("keys", []))
    keys.discard(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def is_sensitive(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Return True if the key is marked sensitive."""
    return key in get_sensitive_keys(vault_path, password, profile)


def redact_sensitive(vault_path: str, password: str, profile: str, env: dict) -> dict:
    """Return a copy of env with sensitive values replaced by '***REDACTED***'."""
    sensitive = set(get_sensitive_keys(vault_path, password, profile))
    return {
        k: ("***REDACTED***" if k in sensitive else v)
        for k, v in env.items()
    }
