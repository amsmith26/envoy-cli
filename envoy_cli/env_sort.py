"""Sort keys within a profile alphabetically or by custom order."""

from typing import Optional
from envoy_cli.vault import load_vault, save_vault


class SortError(Exception):
    pass


def sort_profile(
    vault_path: str,
    password: str,
    profile: str,
    reverse: bool = False,
    keys: Optional[list] = None,
) -> dict:
    """Sort keys in a profile alphabetically.

    Args:
        vault_path: Path to the vault file.
        password: Vault password.
        profile: Profile name to sort.
        reverse: If True, sort in descending order.
        keys: If provided, only sort these specific keys (others remain at end).

    Returns:
        The sorted env dict.
    """
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise SortError(f"Profile '{profile}' not found.")

    env = vault[profile]
    if not isinstance(env, dict):
        raise SortError(f"Profile '{profile}' has invalid data.")

    if keys:
        unknown = [k for k in keys if k not in env]
        if unknown:
            raise SortError(f"Keys not found in profile: {', '.join(unknown)}")
        subset = {k: env[k] for k in sorted(keys, reverse=reverse)}
        remainder = {k: v for k, v in env.items() if k not in keys}
        sorted_env = {**subset, **remainder}
    else:
        sorted_env = dict(sorted(env.items(), key=lambda x: x[0], reverse=reverse))

    vault[profile] = sorted_env
    save_vault(vault_path, password, vault)
    return sorted_env


def preview_sort(
    vault_path: str,
    password: str,
    profile: str,
    reverse: bool = False,
) -> list:
    """Return sorted key order without modifying the vault.

    Returns:
        List of keys in sorted order.
    """
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise SortError(f"Profile '{profile}' not found.")
    env = vault[profile]
    return sorted(env.keys(), reverse=reverse)
