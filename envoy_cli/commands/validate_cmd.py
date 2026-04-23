"""CLI commands for managing and running validation rules on env profiles."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_validate import (
    ValidationRuleError,
    get_rules,
    remove_rule,
    set_rule,
    validate_profile,
)


@click.group("validate")
def validate():
    """Manage and run validation rules for env profiles."""


@validate.command("set-rule")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--type", "vtype", default=None, help="Value type: str, int, float, bool, url, email.")
@click.option("--min-length", default=None, type=int, help="Minimum value length.")
@click.option("--max-length", default=None, type=int, help="Maximum value length.")
def cmd_set_rule(vault_file, password, profile, key, vtype, min_length, max_length):
    """Attach a validation rule to a key in a profile."""
    rule = {}
    if vtype:
        rule["type"] = vtype
    if min_length is not None:
        rule["min_length"] = min_length
    if max_length is not None:
        rule["max_length"] = max_length
    if not rule:
        raise click.UsageError("Provide at least one rule option (--type, --min-length, --max-length).")
    try:
        set_rule(vault_file, password, profile, key, rule)
        click.echo(f"Rule set for '{key}' in profile '{profile}'.")
    except ValidationRuleError as exc:
        raise click.ClickException(str(exc))


@validate.command("remove-rule")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_rule(vault_file, password, profile, key):
    """Remove a validation rule from a key."""
    removed = remove_rule(vault_file, password, profile, key)
    if removed:
        click.echo(f"Rule removed for '{key}' in profile '{profile}'.")
    else:
        click.echo(f"No rule found for '{key}' in profile '{profile}'.")


@validate.command("list-rules")
@vault_options
@click.argument("profile")
def cmd_list_rules(vault_file, password, profile):
    """List all validation rules for a profile."""
    rules = get_rules(vault_file, password, profile)
    if not rules:
        click.echo(f"No validation rules defined for profile '{profile}'.")
        return
    for key, rule in sorted(rules.items()):
        parts = ", ".join(f"{k}={v}" for k, v in rule.items())
        click.echo(f"  {key}: {parts}")


@validate.command("run")
@vault_options
@click.argument("profile")
def cmd_run_validation(vault_file, password, profile):
    """Run all validation rules against a profile's current values."""
    violations = validate_profile(vault_file, password, profile)
    if not violations:
        click.echo(f"All validation rules passed for profile '{profile}'.")
        return
    click.echo(f"Validation failed for profile '{profile}':")
    for v in violations:
        click.echo(f"  [{v.key}] {v.message}")
    raise SystemExit(1)
