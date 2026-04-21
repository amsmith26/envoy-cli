"""CLI commands for key-group management."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.env_group import (
    add_key_to_group,
    remove_key_from_group,
    list_groups,
    get_keys_in_group,
    delete_group,
    GroupError,
)


@click.group("group")
def group():
    """Organise keys into named groups within a profile."""


@group.command("add")
@vault_options
@click.argument("profile")
@click.argument("group_name")
@click.argument("key")
def cmd_add_key(vault, password, profile, group_name, key):
    """Add KEY to GROUP_NAME inside PROFILE."""
    try:
        keys = add_key_to_group(vault, password, profile, group_name, key)
        click.echo(f"Added '{key}' to group '{group_name}'. Keys: {', '.join(keys)}")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@group.command("remove")
@vault_options
@click.argument("profile")
@click.argument("group_name")
@click.argument("key")
def cmd_remove_key(vault, password, profile, group_name, key):
    """Remove KEY from GROUP_NAME inside PROFILE."""
    try:
        remaining = remove_key_from_group(vault, password, profile, group_name, key)
        if remaining:
            click.echo(f"Removed. Remaining keys: {', '.join(remaining)}")
        else:
            click.echo(f"Removed. Group '{group_name}' is now empty and was deleted.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@group.command("list")
@vault_options
@click.argument("profile")
def cmd_list_groups(vault, password, profile):
    """List all groups and their keys for PROFILE."""
    try:
        groups = list_groups(vault, password, profile)
        if not groups:
            click.echo("No groups defined.")
            return
        for g, keys in sorted(groups.items()):
            click.echo(f"{g}: {', '.join(keys)}")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@group.command("show")
@vault_options
@click.argument("profile")
@click.argument("group_name")
def cmd_show_group(vault, password, profile, group_name):
    """Show keys belonging to GROUP_NAME in PROFILE."""
    keys = get_keys_in_group(vault, password, profile, group_name)
    if not keys:
        click.echo(f"Group '{group_name}' is empty or does not exist.")
    else:
        for k in keys:
            click.echo(k)


@group.command("delete")
@vault_options
@click.argument("profile")
@click.argument("group_name")
def cmd_delete_group(vault, password, profile, group_name):
    """Delete GROUP_NAME from PROFILE (keys are kept)."""
    try:
        delete_group(vault, password, profile, group_name)
        click.echo(f"Group '{group_name}' deleted.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
