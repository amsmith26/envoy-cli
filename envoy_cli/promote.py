"""Promote environment variables from one profile to another with optional key filtering."""

from typing import Optional
from envoy_cli.vault import load_vault, save_vault
from envoy_cli.lock import is_locked, LockError


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


def promote_profile(
    vault_file: str,
    password: str,
    source: str,
    target: str,
    keys: Optional[list] = None,
    overwrite: bool = True,
) -> dict:
    """
    Promote variables from source profile into target profile.

    Args:
        vault_file: Path to the vault file.
        password: Vault password.
        source: Name of the source profile.
        target: Name of the target profile.
        keys: Optional list of keys to promote. If None, all keys are promoted.
        overwrite: If True, existing keys in target are overwritten.

    Returns:
        A dict summarising the operation with keys 'promoted', 'skipped'.

    Raises:
        PromoteError: If source profile does not exist.
        LockError: If the target profile is locked.
    """
    vault = load_vault(vault_file, password)

    if source not in vault:
        raise PromoteError(f"Source profile '{source}' does not exist.")

    if is_locked(vault, target):
        raise LockError(f"Target profile '{target}' is locked and cannot be modified.")

    source_env = vault[source]
    target_env = vault.setdefault(target, {})

    candidates = keys if keys is not None else list(source_env.keys())

    promoted = []
    skipped = []

    for key in candidates:
        if key not in source_env:
            skipped.append(key)
            continue
        if not overwrite and key in target_env:
            skipped.append(key)
            continue
        target_env[key] = source_env[key]
        promoted.append(key)

    vault[target] = target_env
    save_vault(vault_file, password, vault)

    return {"promoted": promoted, "skipped": skipped}


def list_promotable_keys(vault_file: str, password: str, source: str, target: str) -> dict:
    """
    Compare source and target profiles to show what would be promoted.

    Returns:
        A dict with 'new' (keys only in source), 'changed' (keys in both but different values),
        'unchanged' (keys in both with same values).
    """
    vault = load_vault(vault_file, password)

    if source not in vault:
        raise PromoteError(f"Source profile '{source}' does not exist.")

    source_env = vault.get(source, {})
    target_env = vault.get(target, {})

    new_keys = [k for k in source_env if k not in target_env]
    changed_keys = [k for k in source_env if k in target_env and source_env[k] != target_env[k]]
    unchanged_keys = [k for k in source_env if k in target_env and source_env[k] == target_env[k]]

    return {"new": sorted(new_keys), "changed": sorted(changed_keys), "unchanged": sorted(unchanged_keys)}
