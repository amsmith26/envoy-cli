"""Format enforcement for env values (e.g., uppercase, lowercase, trim, slug)."""

from __future__ import annotations

RE_SLUG = None  # lazy import

FORMATS = ["uppercase", "lowercase", "strip", "slug", "title"]


class FormatError(Exception):
    pass


def _formats_store(vault: dict) -> dict:
    return vault.setdefault("__formats__", {})


def list_formats() -> list[str]:
    """Return the supported format names."""
    return sorted(FORMATS)


def get_format(vault: dict, profile: str, key: str) -> str | None:
    """Return the assigned format for a key, or None."""
    store = _formats_store(vault)
    return store.get(profile, {}).get(key)


def set_format(vault: dict, profile: str, key: str, fmt: str) -> str:
    """Assign a format rule to a key in a profile."""
    if profile not in vault:
        raise FormatError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise FormatError(f"Key '{key}' not found in profile '{profile}'.")
    if fmt not in FORMATS:
        raise FormatError(f"Unknown format '{fmt}'. Choose from: {', '.join(FORMATS)}.")
    store = _formats_store(vault)
    store.setdefault(profile, {})[key] = fmt
    return fmt


def remove_format(vault: dict, profile: str, key: str) -> bool:
    """Remove a format rule from a key. Returns True if removed, False if not set."""
    store = _formats_store(vault)
    profile_formats = store.get(profile, {})
    if key in profile_formats:
        del profile_formats[key]
        return True
    return False


def apply_format(value: str, fmt: str) -> str:
    """Apply a named format to a string value."""
    if fmt == "uppercase":
        return value.upper()
    if fmt == "lowercase":
        return value.lower()
    if fmt == "strip":
        return value.strip()
    if fmt == "title":
        return value.title()
    if fmt == "slug":
        import re
        value = value.strip().lower()
        value = re.sub(r"[^\w\s-]", "", value)
        value = re.sub(r"[\s_]+", "-", value)
        return value
    raise FormatError(f"Unknown format '{fmt}'.")


def format_profile(vault: dict, profile: str, dry_run: bool = False) -> dict[str, str]:
    """Apply all format rules for a profile. Returns dict of changed keys."""
    if profile not in vault:
        raise FormatError(f"Profile '{profile}' not found.")
    store = _formats_store(vault)
    rules = store.get(profile, {})
    changed: dict[str, str] = {}
    for key, fmt in rules.items():
        if key not in vault[profile]:
            continue
        original = vault[profile][key]
        formatted = apply_format(original, fmt)
        if formatted != original:
            changed[key] = formatted
            if not dry_run:
                vault[profile][key] = formatted
    return changed
