"""CLI commands for env-checkpoint management."""
import click

from envoy_cli.commands import vault_options
from envoy_cli.env_checkpoint import (
    CheckpointError,
    create_checkpoint,
    delete_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)


@click.group("checkpoint")
def checkpoint() -> None:
    """Save and restore named checkpoints for a profile."""


@checkpoint.command("create")
@vault_options
@click.argument("profile")
@click.option("--label", default=None, help="Optional checkpoint label.")
def cmd_create_checkpoint(vault: str, password: str, profile: str, label: str) -> None:
    """Create a checkpoint for PROFILE."""
    try:
        name = create_checkpoint(vault, password, profile, label)
        click.echo(f"Checkpoint '{name}' created for profile '{profile}'.")
    except CheckpointError as exc:
        raise click.ClickException(str(exc))


@checkpoint.command("list")
@vault_options
@click.argument("profile")
def cmd_list_checkpoints(vault: str, password: str, profile: str) -> None:
    """List checkpoints for PROFILE."""
    try:
        entries = list_checkpoints(vault, password, profile)
    except CheckpointError as exc:
        raise click.ClickException(str(exc))
    if not entries:
        click.echo("No checkpoints found.")
        return
    for entry in entries:
        click.echo(f"{entry['label']}  ({entry['created_at']})")


@checkpoint.command("restore")
@vault_options
@click.argument("profile")
@click.argument("label")
def cmd_restore_checkpoint(vault: str, password: str, profile: str, label: str) -> None:
    """Restore PROFILE from checkpoint LABEL."""
    try:
        env = restore_checkpoint(vault, password, profile, label)
        click.echo(f"Restored {len(env)} key(s) from checkpoint '{label}' into '{profile}'.")
    except CheckpointError as exc:
        raise click.ClickException(str(exc))


@checkpoint.command("delete")
@vault_options
@click.argument("profile")
@click.argument("label")
def cmd_delete_checkpoint(vault: str, password: str, profile: str, label: str) -> None:
    """Delete checkpoint LABEL from PROFILE."""
    try:
        remaining = delete_checkpoint(vault, password, profile, label)
        click.echo(f"Deleted checkpoint '{label}'. {len(remaining)} checkpoint(s) remaining.")
    except CheckpointError as exc:
        raise click.ClickException(str(exc))
