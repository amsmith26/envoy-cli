"""Set, unset, and get individual keys within a vault profile."""

from envoy_cli.vault import load_vault, save_vault
from envoy_cli.history import record_change


class EnvSetError(Exception):
    pass


def set_key(vault_path: str, password: str, profile: str, key: str, value: str) -> None:
    """Set a key-value pair in the given profile. Creates profile if absent."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        vault[profile] = {}
    old_value = vault[profile].get(key)
    vault[profile][key] = value
    save_vault(vault_path, password, vault)
    record_change(vault_path, password, profile, key, old_value, value)


def unset_key(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove a key from a profile. Returns True if key existed, False otherwise."""
    vault = load_vault(vault_path, password)
    if profile not in vault or key not in vault[profile]:
        return False
    old_value = vault[profile].pop(key)
    save_vault(vault_path, password, vault)
    record_change(vault_path, password, profile, key, old_value, None)
    return True


def get_key(vault_path: str, password: str, profile: str, key: str) -> str:
    """Retrieve the value for a key in a profile.

    Raises EnvSetError if the profile or key does not exist.
    """
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise EnvSetError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise EnvSetError(f"Key '{key}' not found in profile '{profile}'.")
    return vault[profile][key]


def list_keys(vault_path: str, password: str, profile: str) -> dict:
    """Return all key-value pairs for the given profile."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise EnvSetError(f"Profile '{profile}' not found.")
    return dict(vault[profile])
