"""Key rotation: re-encrypt a vault with a new password."""

from envoy_cli.vault import load_vault, save_vault, vault_exists
from envoy_cli.audit import record_event


def rotate_vault_password(
    vault_file: str,
    old_password: str,
    new_password: str,
) -> list[str]:
    """
    Re-encrypt every profile in *vault_file* under *new_password*.

    Returns the list of profile names that were rotated.
    Raises ValueError if the vault does not exist.
    Raises an exception propagated from load_vault if *old_password* is wrong.
    """
    if not vault_exists(vault_file):
        raise ValueError(f"Vault not found: {vault_file}")

    data = load_vault(vault_file, old_password)
    profiles = list(data.keys())

    save_vault(vault_file, data, new_password)

    record_event(
        vault_file,
        "rotate",
        {"profiles": profiles},
    )

    return profiles
