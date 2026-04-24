"""CLI commands for env-scope management."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_scope import (
    ScopeError,
    get_scopes,
    is_allowed,
    list_restricted_keys,
    remove_scope,
    set_scope,
)


@click.group("scope")
def scope():
    """Manage key access scopes across profiles."""


@scope.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--allow", "allowed", multiple=True, required=True, help="Profile(s) allowed to read this key.")
def cmd_set_scope(vault, password, profile, key, allowed):
    """Restrict KEY in PROFILE to specific profiles."""
    try:
        result = set_scope(vault, password, profile, key, list(allowed))
        click.echo(f"Scope set for '{key}' in '{profile}': {', '.join(result)}")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@scope.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_scope(vault, password, profile, key):
    """Remove scope restriction for KEY in PROFILE."""
    removed = remove_scope(vault, password, profile, key)
    if removed:
        click.echo(f"Scope restriction removed for '{key}' in '{profile}'.")
    else:
        click.echo(f"No scope restriction found for '{key}' in '{profile}'.")


@scope.command("list")
@vault_options
@click.argument("profile")
def cmd_list_scopes(vault, password, profile):
    """List all scope-restricted keys in PROFILE."""
    scopes = get_scopes(vault, password, profile)
    if not scopes:
        click.echo("No scope restrictions defined.")
        return
    for key, allowed in sorted(scopes.items()):
        click.echo(f"{key}: {', '.join(allowed)}")


@scope.command("check")
@vault_options
@click.argument("src_profile")
@click.argument("key")
@click.argument("target_profile")
def cmd_check_scope(vault, password, src_profile, key, target_profile):
    """Check if TARGET_PROFILE may access KEY from SRC_PROFILE."""
    allowed = is_allowed(vault, password, src_profile, key, target_profile)
    status = "allowed" if allowed else "denied"
    click.echo(f"Access for '{target_profile}' to '{key}' in '{src_profile}': {status}")
