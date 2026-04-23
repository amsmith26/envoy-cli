"""CLI commands for managing default key values."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.vault import load_vault, save_vault
from envoy_cli.env_default import (
    set_default,
    get_default,
    remove_default,
    list_defaults,
    apply_defaults,
    DefaultError,
)


@click.group()
def default():
    """Manage default values for environment keys."""


@default.command("set")
@vault_options
@click.argument("key")
@click.argument("value")
def cmd_set_default(vault_file, password, key, value):
    """Set a default value for KEY."""
    vault = load_vault(vault_file, password)
    try:
        set_default(vault, key, value)
    except DefaultError as e:
        raise click.ClickException(str(e))
    save_vault(vault_file, password, vault)
    click.echo(f"Default for '{key}' set to '{value}'.")


@default.command("get")
@vault_options
@click.argument("key")
def cmd_get_default(vault_file, password, key):
    """Get the default value for KEY."""
    vault = load_vault(vault_file, password)
    value = get_default(vault, key)
    if value is None:
        click.echo(f"No default set for '{key}'.")
    else:
        click.echo(value)


@default.command("remove")
@vault_options
@click.argument("key")
def cmd_remove_default(vault_file, password, key):
    """Remove the default value for KEY."""
    vault = load_vault(vault_file, password)
    removed = remove_default(vault, key)
    if not removed:
        raise click.ClickException(f"No default found for '{key}'.")
    save_vault(vault_file, password, vault)
    click.echo(f"Default for '{key}' removed.")


@default.command("list")
@vault_options
def cmd_list_defaults(vault_file, password):
    """List all default values."""
    vault = load_vault(vault_file, password)
    defaults = list_defaults(vault)
    if not defaults:
        click.echo("No defaults set.")
        return
    for key, value in sorted(defaults.items()):
        click.echo(f"{key}={value}")


@default.command("apply")
@vault_options
@click.argument("profile")
def cmd_apply_defaults(vault_file, password, profile):
    """Show PROFILE env with defaults applied for missing keys."""
    vault = load_vault(vault_file, password)
    try:
        merged = apply_defaults(vault, profile)
    except DefaultError as e:
        raise click.ClickException(str(e))
    for key, value in sorted(merged.items()):
        click.echo(f"{key}={value}")
