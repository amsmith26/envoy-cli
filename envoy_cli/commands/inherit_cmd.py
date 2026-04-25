"""CLI commands for profile inheritance."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_inherit import InheritError, get_parent, remove_parent, resolve_inherited, set_parent
from envoy_cli.vault import load_vault


@click.group("inherit")
def inherit() -> None:
    """Manage profile inheritance."""


@inherit.command("set")
@vault_options
@click.argument("profile")
@click.argument("parent")
def cmd_set_parent(vault_file: str, password: str, profile: str, parent: str) -> None:
    """Set PARENT as the inheritance source for PROFILE."""
    try:
        result = set_parent(vault_file, password, profile, parent)
        click.echo(f"Profile '{profile}' now inherits from '{result}'.")
    except InheritError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@inherit.command("remove")
@vault_options
@click.argument("profile")
def cmd_remove_parent(vault_file: str, password: str, profile: str) -> None:
    """Remove the inheritance link for PROFILE."""
    removed = remove_parent(vault_file, password, profile)
    if removed:
        click.echo(f"Inheritance link removed for '{profile}'.")
    else:
        click.echo(f"Profile '{profile}' has no parent set.")


@inherit.command("show")
@vault_options
@click.argument("profile")
def cmd_show_parent(vault_file: str, password: str, profile: str) -> None:
    """Show the parent profile for PROFILE."""
    from envoy_cli.vault import load_vault
    vault = load_vault(vault_file, password)
    parent = get_parent(vault, profile)
    if parent:
        click.echo(f"'{profile}' inherits from '{parent}'.")
    else:
        click.echo(f"'{profile}' has no parent.")


@inherit.command("resolve")
@vault_options
@click.argument("profile")
def cmd_resolve(vault_file: str, password: str, profile: str) -> None:
    """Show the resolved (merged) env for PROFILE after inheritance."""
    try:
        vault = load_vault(vault_file, password)
        env = resolve_inherited(vault, profile)
        for key, value in sorted(env.items()):
            click.echo(f"{key}={value}")
    except InheritError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
