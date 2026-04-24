"""Transform env values using built-in or custom transformations."""

from typing import Optional
from envoy_cli.vault import load_vault, save_vault


class TransformError(Exception):
    pass


BUILTIN_TRANSFORMS = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda v: v[::-1],
    "base64encode": lambda v: __import__("base64").b64encode(v.encode()).decode(),
    "base64decode": lambda v: __import__("base64").b64decode(v.encode()).decode(),
    "urlencode": lambda v: __import__("urllib.parse", fromlist=["quote"]).quote(v, safe=""),
    "urldecode": lambda v: __import__("urllib.parse", fromlist=["unquote"]).unquote(v),
}


def list_transforms() -> list[str]:
    """Return sorted list of available built-in transform names."""
    return sorted(BUILTIN_TRANSFORMS.keys())


def apply_transform(value: str, transform: str) -> str:
    """Apply a named transform to a string value."""
    if transform not in BUILTIN_TRANSFORMS:
        raise TransformError(f"Unknown transform: '{transform}'. Available: {list_transforms()}")
    try:
        return BUILTIN_TRANSFORMS[transform](value)
    except Exception as exc:
        raise TransformError(f"Transform '{transform}' failed: {exc}") from exc


def transform_key(
    vault_file: str,
    password: str,
    profile: str,
    key: str,
    transform: str,
    dry_run: bool = False,
) -> tuple[str, str]:
    """Apply transform to a single key in a profile. Returns (old_value, new_value)."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise TransformError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise TransformError(f"Key '{key}' not found in profile '{profile}'.")
    old_value = vault[profile][key]
    new_value = apply_transform(old_value, transform)
    if not dry_run:
        vault[profile][key] = new_value
        save_vault(vault_file, password, vault)
    return old_value, new_value


def transform_profile(
    vault_file: str,
    password: str,
    profile: str,
    transform: str,
    keys: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict[str, tuple[str, str]]:
    """Apply transform to all (or selected) keys in a profile. Returns {key: (old, new)}."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise TransformError(f"Profile '{profile}' not found.")
    targets = keys if keys else list(vault[profile].keys())
    results = {}
    for k in targets:
        if k not in vault[profile]:
            raise TransformError(f"Key '{k}' not found in profile '{profile}'.")
        old = vault[profile][k]
        new = apply_transform(old, transform)
        results[k] = (old, new)
        if not dry_run:
            vault[profile][k] = new
    if not dry_run:
        save_vault(vault_file, password, vault)
    return results
