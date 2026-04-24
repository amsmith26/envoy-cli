"""CLI commands for archiving and unarchiving profiles."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_archive import (
    ArchiveError,
    archive_profile,
    get_archived_env,
    list_archived,
    unarchive_profile,
)


@click.group("archive")
def archive() -> None:
    """Archive and restore profiles."""


@archive.command("add")
@vault_options
@click.argument("profile")
def cmd_archive_profile(vault: str, password: str, profile: str) -> None:
    """Archive PROFILE (removes it from active profiles)."""
    try:
        remaining = archive_profile(vault, password, profile)
        click.echo(f"Archived '{profile}'.")
        if remaining:
            click.echo("Archived profiles: " + ", ".join(remaining))
    except ArchiveError as exc:
        raise click.ClickException(str(exc))


@archive.command("restore")
@vault_options
@click.argument("profile")
def cmd_unarchive_profile(vault: str, password: str, profile: str) -> None:
    """Restore PROFILE from the archive."""
    try:
        unarchive_profile(vault, password, profile)
        click.echo(f"Restored '{profile}' from archive.")
    except ArchiveError as exc:
        raise click.ClickException(str(exc))


@archive.command("list")
@vault_options
def cmd_list_archived(vault: str, password: str) -> None:
    """List all archived profiles."""
    profiles = list_archived(vault, password)
    if not profiles:
        click.echo("No archived profiles.")
    else:
        for p in profiles:
            click.echo(p)


@archive.command("show")
@vault_options
@click.argument("profile")
def cmd_show_archived(vault: str, password: str, profile: str) -> None:
    """Show env vars of an archived PROFILE without restoring it."""
    try:
        env = get_archived_env(vault, password, profile)
        for key, value in sorted(env.items()):
            click.echo(f"{key}={value}")
    except ArchiveError as exc:
        raise click.ClickException(str(exc))
