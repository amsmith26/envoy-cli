"""Schema validation for .env profiles."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


class SchemaValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Schema validation failed:\n" + "\n".join(errors))


def load_schema(schema_path: str | Path) -> dict[str, Any]:
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with open(path) as f:
        return json.load(f)


def validate_env(env: dict[str, str], schema: dict[str, Any]) -> list[str]:
    """Validate env dict against a schema. Returns list of error messages."""
    errors: list[str] = []
    fields: dict[str, Any] = schema.get("fields", {})

    for key, rules in fields.items():
        required = rules.get("required", False)
        pattern = rules.get("pattern")
        allowed = rules.get("allowed_values")
        min_len = rules.get("min_length")

        if key not in env:
            if required:
                errors.append(f"Missing required key: {key}")
            continue

        value = env[key]

        if not value and required:
            errors.append(f"Required key '{key}' has empty value")

        if pattern:
            import re
            if not re.fullmatch(pattern, value):
                errors.append(f"Key '{key}' value '{value}' does not match pattern '{pattern}'")

        if allowed and value not in allowed:
            errors.append(f"Key '{key}' value '{value}' not in allowed values {allowed}")

        if min_len is not None and len(value) < min_len:
            errors.append(f"Key '{key}' value too short (min {min_len} chars)")

    return errors


def validate_or_raise(env: dict[str, str], schema: dict[str, Any]) -> None:
    errors = validate_env(env, schema)
    if errors:
        raise SchemaValidationError(errors)
