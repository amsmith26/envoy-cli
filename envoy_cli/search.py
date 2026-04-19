"""Search across vault profiles for keys or values."""

from typing import Optional
from envoy_cli.vault import load_vault


def search_by_key(
    vault_file: str,
    password: str,
    pattern: str,
    case_sensitive: bool = False,
) -> dict[str, dict[str, str]]:
    """Return {profile: {key: value}} where key matches pattern."""
    data = load_vault(vault_file, password)
    results: dict[str, dict[str, str]] = {}
    needle = pattern if case_sensitive else pattern.lower()
    for profile, env in data.items():
        if profile == "__snapshots__":
            continue
        matches = {
            k: v
            for k, v in env.items()
            if needle in (k if case_sensitive else k.lower())
        }
        if matches:
            results[profile] = matches
    return results


def search_by_value(
    vault_file: str,
    password: str,
    pattern: str,
    case_sensitive: bool = False,
) -> dict[str, dict[str, str]]:
    """Return {profile: {key: value}} where value matches pattern."""
    data = load_vault(vault_file, password)
    results: dict[str, dict[str, str]] = {}
    needle = pattern if case_sensitive else pattern.lower()
    for profile, env in data.items():
        if profile == "__snapshots__":
            continue
        matches = {
            k: v
            for k, v in env.items()
            if needle in (v if case_sensitive else v.lower())
        }
        if matches:
            results[profile] = matches
    return results


def search_env(
    vault_file: str,
    password: str,
    pattern: str,
    mode: str = "key",
    case_sensitive: bool = False,
) -> dict[str, dict[str, str]]:
    """Dispatch search by mode: 'key' or 'value'."""
    if mode == "key":
        return search_by_key(vault_file, password, pattern, case_sensitive)
    elif mode == "value":
        return search_by_value(vault_file, password, pattern, case_sensitive)
    else:
        raise ValueError(f"Unknown search mode: {mode!r}. Use 'key' or 'value'.")
