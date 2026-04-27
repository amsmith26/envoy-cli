"""CLI commands for renaming profiles."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.env_rename_profile import rename_profile, list_profile_names, RenameProfileError


@click.group("rename-profile")
def rename_profile_group():
    """Rename profiles within a vault."""


@rename_profile_group.command("run")
@vault_options
@click.argument("old_name")
@click.argument("new_name")
def cmd_rename_profile(vault, password, old_name, new_name):
    """Rename OLD_NAME profile to NEW_NAME."""
    try:
        result = rename_profile(vault, password, old_name, new_name)
        click.echo(f"Profile renamed: '{old_name}' → '{result}'")
    except RenameProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rename_profile_group.command("list")
@vault_options
def cmd_list_profiles(vault, password):
    """List all profile names in the vault."""
    try:
        names = list_profile_names(vault, password)
        if not names:
            click.echo("No profiles found.")
        else:
            for name in names:
                click.echo(name)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
