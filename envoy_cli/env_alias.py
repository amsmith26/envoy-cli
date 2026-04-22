"""Alias management: create short names that point to existing env keys."""

from __future__ import annotations

from envoy_cli.vault import load_vault, save_vault


class AliasError(Exception):
    pass


def _aliases_store(vault: dict) -> dict:
    return vault.setdefault("__aliases__", {})


def get_aliases(vault_path: str, password: str) -> dict[str, dict[str, str]]:
    """Return all aliases keyed by profile."""
    vault = load_vault(vault_path, password)
    return dict(_aliases_store(vault))


def add_alias(
    vault_path: str,
    password: str,
    profile: str,
    alias: str,
    target_key: str,
) -> str:
    """Create *alias* pointing to *target_key* in *profile*.

    Raises AliasError if the profile or target key does not exist,
    or if the alias name is already used as a real key.
    """
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise AliasError(f"Profile '{profile}' not found.")
    env = vault[profile]
    if target_key not in env:
        raise AliasError(f"Key '{target_key}' not found in profile '{profile}'.")
    if alias in env:
        raise AliasError(
            f"'{alias}' already exists as a real key in profile '{profile}'."
        )
    store = _aliases_store(vault)
    profile_aliases = store.setdefault(profile, {})
    profile_aliases[alias] = target_key
    save_vault(vault, vault_path, password)
    return target_key


def remove_alias(
    vault_path: str, password: str, profile: str, alias: str
) -> bool:
    """Remove *alias* from *profile*. Returns True if removed, False if not found."""
    vault = load_vault(vault_path, password)
    store = _aliases_store(vault)
    profile_aliases = store.get(profile, {})
    if alias not in profile_aliases:
        return False
    del profile_aliases[alias]
    save_vault(vault, vault_path, password)
    return True


def resolve_alias(
    vault_path: str, password: str, profile: str, alias: str
) -> str | None:
    """Return the value of the key that *alias* points to, or None."""
    vault = load_vault(vault_path, password)
    store = _aliases_store(vault)
    target_key = store.get(profile, {}).get(alias)
    if target_key is None:
        return None
    return vault.get(profile, {}).get(target_key)


def list_aliases(vault_path: str, password: str, profile: str) -> dict[str, str]:
    """Return alias->target_key mapping for *profile*."""
    vault = load_vault(vault_path, password)
    return dict(_aliases_store(vault).get(profile, {}))
