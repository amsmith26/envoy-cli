"""Tag profiles with labels for organization and filtering."""
from __future__ import annotations
from envoy_cli.vault import load_vault, save_vault


class TagError(Exception):
    pass


def _tags_key() -> str:
    return "__tags__"


def get_tags(vault: dict, profile: str) -> list[str]:
    """Return tags for a profile."""
    tags_store = vault.get(_tags_key(), {})
    return list(tags_store.get(profile, []))


def add_tag(vault: dict, profile: str, tag: str) -> list[str]:
    """Add a tag to a profile. Returns updated tag list."""
    if profile not in vault and profile != _tags_key():
        existing = [k for k in vault if not k.startswith("__")]
        if profile not in existing:
            raise TagError(f"Profile '{profile}' does not exist.")
    tags_store = vault.setdefault(_tags_key(), {})
    current = set(tags_store.get(profile, []))
    current.add(tag)
    tags_store[profile] = sorted(current)
    return tags_store[profile]


def remove_tag(vault: dict, profile: str, tag: str) -> list[str]:
    """Remove a tag from a profile. Returns updated tag list."""
    tags_store = vault.get(_tags_key(), {})
    current = set(tags_store.get(profile, []))
    if tag not in current:
        raise TagError(f"Tag '{tag}' not found on profile '{profile}'.")
    current.discard(tag)
    tags_store[profile] = sorted(current)
    return tags_store[profile]


def list_profiles_by_tag(vault: dict, tag: str) -> list[str]:
    """Return all profiles that have the given tag."""
    tags_store = vault.get(_tags_key(), {})
    return sorted(p for p, tags in tags_store.items() if tag in tags)


def clear_tags(vault: dict, profile: str) -> None:
    """Remove all tags from a profile."""
    tags_store = vault.get(_tags_key(), {})
    tags_store.pop(profile, None)
