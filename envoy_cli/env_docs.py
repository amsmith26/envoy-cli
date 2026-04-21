"""Inline documentation/annotations for env keys stored in the vault."""

from __future__ import annotations

from typing import Optional

from envoy_cli.vault import load_vault, save_vault

_DOCS_KEY = "__docs__"


class DocError(Exception):
    pass


def _docs_store(vault: dict, profile: str) -> dict:
    return vault.setdefault(profile, {}).setdefault(_DOCS_KEY, {})


def get_doc(vault_path: str, password: str, profile: str, key: str) -> Optional[str]:
    """Return the doc string for *key* in *profile*, or None if absent."""
    vault = load_vault(vault_path, password)
    return _docs_store(vault, profile).get(key)


def set_doc(
    vault_path: str, password: str, profile: str, key: str, doc: str
) -> str:
    """Attach *doc* to *key* in *profile*. Returns the stored doc string."""
    vault = load_vault(vault_path, password)
    env = vault.get(profile, {})
    if key not in env and key != _DOCS_KEY:
        raise DocError(f"Key '{key}' not found in profile '{profile}'.")
    _docs_store(vault, profile)[key] = doc
    save_vault(vault_path, password, vault)
    return doc


def remove_doc(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove the doc for *key*. Returns True if a doc existed."""
    vault = load_vault(vault_path, password)
    store = _docs_store(vault, profile)
    if key in store:
        del store[key]
        save_vault(vault_path, password, vault)
        return True
    return False


def list_docs(vault_path: str, password: str, profile: str) -> dict[str, str]:
    """Return all key→doc mappings for *profile*."""
    vault = load_vault(vault_path, password)
    return dict(_docs_store(vault, profile))
