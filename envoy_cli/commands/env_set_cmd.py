"""CLI commands for setting, unsetting, and getting individual env keys."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.env_set import set_key, unset_key, get_key, list_keys, EnvSetError


@click.group()
def env_set():
    """Get, set, or unset individual keys in a vault profile."""


@env_set.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("value")
def cmd_set_key(vault, password, profile, key, value):
    """Set KEY=VALUE in PROFILE."""
    try:
        set_key(vault, password, profile, key, value)
        click.echo(f"Set {key} in profile '{profile}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@env_set.command("unset")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_unset_key(vault, password, profile, key):
    """Remove KEY from PROFILE."""
    try:
        removed = unset_key(vault, password, profile, key)
        if removed:
            click.echo(f"Unset '{key}' from profile '{profile}'.")
        else:
            click.echo(f"Key '{key}' not found in profile '{profile}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@env_set.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_key(vault, password, profile, key):
    """Print the value of KEY in PROFILE."""
    try:
        value = get_key(vault, password, profile, key)
        click.echo(value)
    except EnvSetError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@env_set.command("list")
@vault_options
@click.argument("profile")
def cmd_list_keys(vault, password, profile):
    """List all keys in PROFILE."""
    try:
        pairs = list_keys(vault, password, profile)
        if not pairs:
            click.echo(f"Profile '{profile}' is empty.")
        else:
            for k, v in sorted(pairs.items()):
                click.echo(f"{k}={v}")
    except EnvSetError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
