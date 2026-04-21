"""Copy individual keys between profiles in the vault."""

from envoy_cli.vault import load_vault, save_vault


class EnvCopyError(Exception):
    pass


def copy_key(
    vault_path: str,
    password: str,
    src_profile: str,
    dst_profile: str,
    key: str,
    overwrite: bool = False,
) -> str:
    """Copy a single key from src_profile to dst_profile.

    Returns the value that was copied.
    Raises EnvCopyError if the source key is missing or destination key
    already exists and overwrite is False.
    """
    vault = load_vault(vault_path, password)

    if src_profile not in vault:
        raise EnvCopyError(f"Source profile '{src_profile}' not found.")
    if key not in vault[src_profile]:
        raise EnvCopyError(f"Key '{key}' not found in profile '{src_profile}'.")

    value = vault[src_profile][key]

    if dst_profile not in vault:
        vault[dst_profile] = {}

    if key in vault[dst_profile] and not overwrite:
        raise EnvCopyError(
            f"Key '{key}' already exists in profile '{dst_profile}'. "
            "Use overwrite=True to replace it."
        )

    vault[dst_profile][key] = value
    save_vault(vault_path, password, vault)
    return value


def copy_keys(
    vault_path: str,
    password: str,
    src_profile: str,
    dst_profile: str,
    keys: list[str],
    overwrite: bool = False,
) -> dict[str, str]:
    """Copy multiple keys from src_profile to dst_profile.

    Returns a dict of {key: value} for all keys that were copied.
    """
    vault = load_vault(vault_path, password)

    if src_profile not in vault:
        raise EnvCopyError(f"Source profile '{src_profile}' not found.")
    if dst_profile not in vault:
        vault[dst_profile] = {}

    copied = {}
    for key in keys:
        if key not in vault[src_profile]:
            raise EnvCopyError(f"Key '{key}' not found in profile '{src_profile}'.")
        if key in vault[dst_profile] and not overwrite:
            raise EnvCopyError(
                f"Key '{key}' already exists in profile '{dst_profile}'. "
                "Use overwrite=True to replace it."
            )
        copied[key] = vault[src_profile][key]
        vault[dst_profile][key] = copied[key]

    save_vault(vault_path, password, vault)
    return copied
