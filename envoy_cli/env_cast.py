"""Type casting utilities for env variable values."""

from __future__ import annotations

from typing import Any

from envoy_cli.vault import load_vault, save_vault


class CastError(Exception):
    pass


SUPPORTED_TYPES = ("str", "int", "float", "bool")


def _casts_store(vault: dict) -> dict:
    return vault.setdefault("__casts__", {})


def cast_value(value: str, type_name: str) -> Any:
    """Cast a string value to the given type name."""
    if type_name not in SUPPORTED_TYPES:
        raise CastError(f"Unsupported type '{type_name}'. Choose from: {', '.join(SUPPORTED_TYPES)}")
    if type_name == "str":
        return value
    if type_name == "int":
        try:
            return int(value)
        except ValueError:
            raise CastError(f"Cannot cast '{value}' to int")
    if type_name == "float":
        try:
            return float(value)
        except ValueError:
            raise CastError(f"Cannot cast '{value}' to float")
    if type_name == "bool":
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise CastError(f"Cannot cast '{value}' to bool")


def set_cast(vault_file: str, password: str, profile: str, key: str, type_name: str) -> str:
    """Record a cast rule for a key in a profile."""
    if type_name not in SUPPORTED_TYPES:
        raise CastError(f"Unsupported type '{type_name}'. Choose from: {', '.join(SUPPORTED_TYPES)}")
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise CastError(f"Profile '{profile}' not found")
    if key not in vault[profile]:
        raise CastError(f"Key '{key}' not found in profile '{profile}'")
    store = _casts_store(vault)
    store.setdefault(profile, {})[key] = type_name
    save_vault(vault_file, password, vault)
    return type_name


def get_cast(vault_file: str, password: str, profile: str, key: str) -> str | None:
    """Return the cast type for a key, or None if not set."""
    vault = load_vault(vault_file, password)
    return _casts_store(vault).get(profile, {}).get(key)


def remove_cast(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Remove a cast rule. Returns True if removed, False if not found."""
    vault = load_vault(vault_file, password)
    store = _casts_store(vault)
    if key in store.get(profile, {}):
        del store[profile][key]
        save_vault(vault_file, password, vault)
        return True
    return False


def list_casts(vault_file: str, password: str, profile: str) -> dict[str, str]:
    """Return all cast rules for a profile."""
    vault = load_vault(vault_file, password)
    return dict(_casts_store(vault).get(profile, {}))


def apply_casts(vault_file: str, password: str, profile: str) -> dict[str, Any]:
    """Return env dict with cast values applied where rules exist."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise CastError(f"Profile '{profile}' not found")
    env = {k: v for k, v in vault[profile].items() if not k.startswith("__")}
    casts = _casts_store(vault).get(profile, {})
    result = {}
    for k, v in env.items():
        if k in casts:
            result[k] = cast_value(v, casts[k])
        else:
            result[k] = v
    return result
