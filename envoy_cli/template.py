"""Template rendering: substitute env vars into template strings."""
from __future__ import annotations
import re
from typing import Optional

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template: str, env: dict[str, str], strict: bool = False) -> str:
    """Replace {{KEY}} placeholders with values from env.

    Args:
        template: Template string with {{KEY}} placeholders.
        env: Mapping of variable names to values.
        strict: If True, raise KeyError for missing keys.

    Returns:
        Rendered string.
    """
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in env:
            if strict:
                raise KeyError(f"Template variable '{key}' not found in env")
            return match.group(0)
        return env[key]

    return _PLACEHOLDER.sub(replacer, template)


def render_file(template_path: str, env: dict[str, str], strict: bool = False) -> str:
    """Read a template file and render it against env."""
    with open(template_path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return render_template(content, env, strict=strict)


def collect_placeholders(template: str) -> list[str]:
    """Return sorted unique list of placeholder keys found in template."""
    return sorted(set(_PLACEHOLDER.findall(template)))
