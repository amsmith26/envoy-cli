"""Trim whitespace from env values in a profile."""

from __future__ import annotations

from typing import Dict, List, Optional

from envoy_cli.vault import load_vault, save_vault


class TrimError(Exception):
    pass


def trim_profile(
    vault_path: str,
    password: str,
    profile: str,
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Trim leading/trailing whitespace from values in *profile*.

    Args:
        vault_path: Path to the vault file.
        password:   Vault password.
        profile:    Profile name to operate on.
        keys:       Optional list of keys to restrict trimming to.
                    If None, all keys are trimmed.
        dry_run:    When True the vault is not modified; only the
                    diff dict is returned.

    Returns:
        A dict mapping key -> trimmed_value for every key that changed.

    Raises:
        TrimError: If the profile does not exist.
    """
    vault = load_vault(vault_path, password)

    if profile not in vault:
        raise TrimError(f"Profile '{profile}' not found.")

    env: Dict[str, str] = vault[profile]
    target_keys = keys if keys is not None else list(env.keys())

    changed: Dict[str, str] = {}
    for key in target_keys:
        if key not in env:
            continue
        trimmed = env[key].strip()
        if trimmed != env[key]:
            changed[key] = trimmed

    if changed and not dry_run:
        for key, value in changed.items():
            env[key] = value
        vault[profile] = env
        save_vault(vault_path, password, vault)

    return changed


def preview_trim(
    vault_path: str,
    password: str,
    profile: str,
    keys: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Return what *trim_profile* would change without persisting."""
    return trim_profile(vault_path, password, profile, keys=keys, dry_run=True)
