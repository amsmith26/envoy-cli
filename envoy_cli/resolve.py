"""Resolve variable references within an env profile (e.g. VAR=${OTHER})."""

import re
from typing import Dict, List, Optional

REF_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class ResolveError(Exception):
    """Raised when variable resolution fails."""


def find_references(value: str) -> List[str]:
    """Return all variable names referenced inside a value string."""
    return REF_PATTERN.findall(value)


def resolve_env(
    env: Dict[str, str],
    strict: bool = True,
    max_depth: int = 10,
) -> Dict[str, str]:
    """Return a new dict with all ${VAR} references expanded.

    Args:
        env: The flat key/value env dict to resolve.
        strict: If True, raise ResolveError for undefined references.
                If False, leave unresolvable placeholders as-is.
        max_depth: Maximum substitution passes before giving up (guards
                   against circular references).

    Returns:
        A new dict with references expanded.

    Raises:
        ResolveError: On circular or undefined references when strict=True.
    """
    resolved = dict(env)

    for _ in range(max_depth):
        changed = False
        for key, value in resolved.items():
            refs = find_references(value)
            if not refs:
                continue
            new_value = value
            for ref in refs:
                if ref in resolved and not find_references(resolved[ref]):
                    new_value = new_value.replace(f"${{{ref}}}", resolved[ref])
                    changed = True
                elif ref not in resolved:
                    if strict:
                        raise ResolveError(
                            f"Key '{key}' references undefined variable '${{{ref}}}'"
                        )
            resolved[key] = new_value

        if not changed:
            break
    else:
        # Check for remaining references (circular)
        for key, value in resolved.items():
            if find_references(value):
                raise ResolveError(
                    f"Circular or unresolvable reference detected in key '{key}': {value}"
                )

    return resolved


def list_unresolved(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of key -> list of unresolved references."""
    try:
        resolved = resolve_env(env, strict=False)
    except ResolveError:
        resolved = dict(env)
    return {
        key: find_references(value)
        for key, value in resolved.items()
        if find_references(value)
    }
