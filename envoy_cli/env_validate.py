"""Runtime validation rules for env values (type, range, length checks)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from envoy_cli.vault import load_vault, save_vault


class ValidationRuleError(Exception):
    pass


SUPPORTED_TYPES = {"str", "int", "float", "bool", "url", "email"}

_RULES_KEY = "__validation_rules__"

_URL_RE = re.compile(r"^https?://[^\s]+$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class RuleViolation:
    key: str
    message: str


def _rules_store(vault: dict) -> dict:
    return vault.setdefault(_RULES_KEY, {})


def get_rules(vault_file: str, password: str, profile: str) -> dict:
    vault = load_vault(vault_file, password)
    return _rules_store(vault).get(profile, {})


def set_rule(vault_file: str, password: str, profile: str, key: str, rule: dict) -> dict:
    vault = load_vault(vault_file, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise ValidationRuleError(f"Profile '{profile}' not found.")
    if key not in profiles[profile]:
        raise ValidationRuleError(f"Key '{key}' not found in profile '{profile}'.")
    vtype = rule.get("type")
    if vtype and vtype not in SUPPORTED_TYPES:
        raise ValidationRuleError(f"Unsupported type '{vtype}'. Choose from: {sorted(SUPPORTED_TYPES)}.")
    store = _rules_store(vault)
    store.setdefault(profile, {})[key] = rule
    save_vault(vault_file, password, vault)
    return rule


def remove_rule(vault_file: str, password: str, profile: str, key: str) -> bool:
    vault = load_vault(vault_file, password)
    store = _rules_store(vault)
    removed = store.get(profile, {}).pop(key, None) is not None
    if removed:
        save_vault(vault_file, password, vault)
    return removed


def validate_profile(vault_file: str, password: str, profile: str) -> list[RuleViolation]:
    vault = load_vault(vault_file, password)
    env = vault.get("profiles", {}).get(profile, {})
    rules = _rules_store(vault).get(profile, {})
    violations: list[RuleViolation] = []
    for key, rule in rules.items():
        value = env.get(key, "")
        violations.extend(_apply_rule(key, value, rule))
    return violations


def _apply_rule(key: str, value: str, rule: dict) -> list[RuleViolation]:
    violations: list[RuleViolation] = []
    vtype = rule.get("type")
    if vtype:
        ok, msg = _check_type(value, vtype)
        if not ok:
            violations.append(RuleViolation(key, f"Expected type '{vtype}': {msg}"))
    min_len = rule.get("min_length")
    if min_len is not None and len(value) < int(min_len):
        violations.append(RuleViolation(key, f"Value too short (min {min_len} chars)."))
    max_len = rule.get("max_length")
    if max_len is not None and len(value) > int(max_len):
        violations.append(RuleViolation(key, f"Value too long (max {max_len} chars)."))
    return violations


def _check_type(value: str, vtype: str) -> tuple[bool, str]:
    if vtype == "int":
        try:
            int(value)
        except ValueError:
            return False, f"'{value}' is not a valid integer."
    elif vtype == "float":
        try:
            float(value)
        except ValueError:
            return False, f"'{value}' is not a valid float."
    elif vtype == "bool":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            return False, f"'{value}' is not a valid boolean."
    elif vtype == "url":
        if not _URL_RE.match(value):
            return False, f"'{value}' is not a valid URL."
    elif vtype == "email":
        if not _EMAIL_RE.match(value):
            return False, f"'{value}' is not a valid email."
    return True, ""
