"""Manage default values for environment keys across profiles."""

from envoy_cli.vault import load_vault, save_vault


class DefaultError(Exception):
    pass


def _defaults_store(vault: dict) -> dict:
    return vault.setdefault("__defaults__", {})


def get_default(vault: dict, key: str) -> str | None:
    """Return the default value for a key, or None if not set."""
    return _defaults_store(vault).get(key)


def set_default(vault: dict, key: str, value: str) -> str:
    """Set a default value for a key. Key must exist in at least one profile."""
    all_keys = {
        k
        for profile, data in vault.items()
        if not profile.startswith("__")
        for k in data.keys()
    }
    if key not in all_keys:
        raise DefaultError(f"Key '{key}' not found in any profile.")
    _defaults_store(vault)[key] = value
    return value


def remove_default(vault: dict, key: str) -> bool:
    """Remove the default value for a key. Returns True if removed, False if not found."""
    store = _defaults_store(vault)
    if key not in store:
        return False
    del store[key]
    return True


def list_defaults(vault: dict) -> dict:
    """Return all default values as a dict."""
    return dict(_defaults_store(vault))


def apply_defaults(vault: dict, profile: str) -> dict:
    """Return the profile env with missing keys filled in from defaults."""
    if profile not in vault or profile.startswith("__"):
        raise DefaultError(f"Profile '{profile}' not found.")
    defaults = _defaults_store(vault)
    merged = dict(defaults)
    merged.update(vault[profile])
    return merged
