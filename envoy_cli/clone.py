"""Clone a profile to a new name, optionally overriding values."""

from envoy_cli.vault import load_vault, save_vault


class CloneError(Exception):
    pass


def clone_profile(
    vault_file: str,
    password: str,
    source: str,
    dest: str,
    overrides: dict | None = None,
) -> dict:
    """Clone source profile into dest, applying optional overrides.

    Returns the cloned env dict.
    """
    vault = load_vault(vault_file, password)

    if source not in vault:
        raise CloneError(f"Source profile '{source}' does not exist.")

    if dest in vault:
        raise CloneError(f"Destination profile '{dest}' already exists.")

    cloned = dict(vault[source])

    if overrides:
        cloned.update(overrides)

    vault[dest] = cloned
    save_vault(vault_file, password, vault)

    return cloned


def list_clone_sources(vault_file: str, password: str) -> list[str]:
    """Return all profile names available to clone."""
    vault = load_vault(vault_file, password)
    return sorted(vault.keys())
