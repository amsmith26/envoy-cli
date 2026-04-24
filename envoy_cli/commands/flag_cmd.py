"""CLI commands for managing boolean flags on env keys."""

from __future__ import annotations

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_flag import FlagError, get_flags, list_flagged_keys, remove_flag, set_flag


@click.group()
def flag():
    """Manage boolean flags on env keys."""


@flag.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--on/--off", default=True, show_default=True, help="Flag value to set.")
def cmd_set_flag(vault, password, profile, key, on):
    """Set a boolean flag on KEY in PROFILE."""
    try:
        result = set_flag(vault, password, profile, key, on)
        state = "ON" if result else "OFF"
        click.echo(f"Flag for '{key}' in '{profile}' set to {state}.")
    except FlagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@flag.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_flag(vault, password, profile, key):
    """Remove a flag from KEY in PROFILE."""
    removed = remove_flag(vault, password, profile, key)
    if removed:
        click.echo(f"Flag removed from '{key}' in '{profile}'.")
    else:
        click.echo(f"No flag set for '{key}' in '{profile}'.")


@flag.command("list")
@vault_options
@click.argument("profile")
@click.option("--on", "filter_val", flag_value=True, default=None, help="Show only ON flags.")
@click.option("--off", "filter_val", flag_value=False, help="Show only OFF flags.")
def cmd_list_flags(vault, password, profile, filter_val):
    """List flagged keys in PROFILE."""
    keys = list_flagged_keys(vault, password, profile, value=filter_val)
    if not keys:
        click.echo("No flags found.")
        return
    flags = get_flags(vault, password, profile)
    for k in keys:
        state = "ON" if flags[k] else "OFF"
        click.echo(f"  {k}: {state}")
