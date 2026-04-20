"""Merge two or more profiles into a target profile."""

from typing import Optional
from envoy_cli.vault import load_vault, save_vault


class MergeError(Exception):
    pass


def merge_profiles(
    vault_path: str,
    password: str,
    sources: list[str],
    target: str,
    overwrite: bool = False,
    keys: Optional[list[str]] = None,
) -> dict[str, list[str]]:
    """Merge one or more source profiles into a target profile.

    Args:
        vault_path: Path to the vault file.
        password: Vault password.
        sources: List of source profile names to merge from (applied left to right).
        target: Name of the target profile to merge into.
        overwrite: If True, source values overwrite existing target values.
        keys: Optional list of keys to restrict the merge to.

    Returns:
        A dict with 'added' and 'updated' key lists.
    """
    vault = load_vault(vault_path, password)

    for source in sources:
        if source not in vault:
            raise MergeError(f"Source profile '{source}' not found in vault.")

    if target not in vault:
        vault[target] = {}

    added: list[str] = []
    updated: list[str] = []

    for source in sources:
        source_env = vault[source]
        for key, value in source_env.items():
            if keys is not None and key not in keys:
                continue
            if key not in vault[target]:
                vault[target][key] = value
                added.append(key)
            elif overwrite and vault[target][key] != value:
                vault[target][key] = value
                updated.append(key)

    save_vault(vault_path, password, vault)
    return {"added": sorted(set(added)), "updated": sorted(set(updated))}


def list_merge_candidates(
    vault_path: str,
    password: str,
    source: str,
    target: str,
) -> dict[str, list[str]]:
    """Preview what would be added or updated in a merge without applying it."""
    vault = load_vault(vault_path, password)

    if source not in vault:
        raise MergeError(f"Source profile '{source}' not found in vault.")

    target_env = vault.get(target, {})
    source_env = vault[source]

    would_add = sorted(k for k in source_env if k not in target_env)
    would_update = sorted(
        k for k in source_env
        if k in target_env and target_env[k] != source_env[k]
    )
    return {"would_add": would_add, "would_update": would_update}
