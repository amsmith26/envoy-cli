"""Lint .env files for common issues."""

from typing import Dict, List


LINT_RULES = [
    "empty_value",
    "duplicate_key",
    "invalid_key",
    "unquoted_special_chars",
]


def lint_env(env: Dict[str, str], raw_lines: List[str] = None) -> List[Dict]:
    """Run all lint checks and return list of issues."""
    issues = []
    issues.extend(_check_empty_values(env))
    issues.extend(_check_invalid_keys(env))
    if raw_lines is not None:
        issues.extend(_check_duplicate_keys(raw_lines))
        issues.extend(_check_unquoted_special_chars(raw_lines))
    return issues


def _check_empty_values(env: Dict[str, str]) -> List[Dict]:
    return [
        {"rule": "empty_value", "key": k, "message": f"'{k}' has an empty value"}
        for k, v in env.items()
        if v == ""
    ]


def _check_invalid_keys(env: Dict[str, str]) -> List[Dict]:
    import re
    pattern = re.compile(r'^[A-Z_][A-Z0-9_]*$')
    return [
        {"rule": "invalid_key", "key": k, "message": f"'{k}' is not a valid env key (use UPPER_SNAKE_CASE)"}
        for k in env
        if not pattern.match(k)
    ]


def _check_duplicate_keys(raw_lines: List[str]) -> List[Dict]:
    seen = {}
    issues = []
    for i, line in enumerate(raw_lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in seen:
                issues.append({"rule": "duplicate_key", "key": key, "message": f"'{key}' is defined multiple times (first at line {seen[key]}, again at line {i})"})
            else:
                seen[key] = i
    return issues


def _check_unquoted_special_chars(raw_lines: List[str]) -> List[Dict]:
    import re
    issues = []
    special = re.compile(r'[\s#$&|<>]')
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        if value and not (value.startswith('"') or value.startswith("'")) and special.search(value):
            issues.append({"rule": "unquoted_special_chars", "key": key.strip(), "message": f"'{key.strip()}' value contains special characters but is not quoted"})
    return issues


def format_lint_results(issues: List[Dict]) -> str:
    if not issues:
        return "No issues found."
    lines = []
    for issue in issues:
        lines.append(f"  [{issue['rule']}] {issue['message']}")
    return "\n".join(lines)
