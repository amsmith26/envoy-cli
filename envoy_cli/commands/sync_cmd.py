"""CLI commands for syncing .env files with vault profiles."""

import click
from pathlib import Path

from envoy_cli.sync import push_env, pull_env, list_profiles, delete_profile


@click.group()
def sync():
    """Sync .env files with vault profiles."""
    pass


@sync.command("push")
@click.option("--env", "env_path", default=".env", show_default=True, help="Path to .env file.")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--profile", required=True, help="Profile name to push to.")
@click.password_option("--password", prompt="Vault password")
def cmd_push(env_path, vault_path, profile, password):
    """Push local .env into a vault profile."""
    push_env(Path(env_path), Path(vault_path), password, profile)
    click.echo(f"Pushed '{env_path}' to profile '{profile}'.")


@sync.command("pull")
@click.option("--env", "env_path", default=".env", show_default=True)
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--profile", required=True, help="Profile name to pull from.")
@click.option("--merge", is_flag=True, default=False, help="Merge with existing local .env.")
@click.option("--no-backup", is_flag=True, default=False, help="Skip backup before overwrite.")
@click.option("--password", prompt=True, hide_input=True)
def cmd_pull(env_path, vault_path, profile, merge, no_backup, password):
    """Pull a vault profile into local .env."""
    try:
        pull_env(Path(env_path), Path(vault_path), password, profile, merge=merge, backup=not no_backup)
        click.echo(f"Pulled profile '{profile}' into '{env_path}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@sync.command("list")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_list(vault_path, password):
    """List all profiles stored in the vault."""
    profiles = list_profiles(Path(vault_path), password)
    if not profiles:
        click.echo("No profiles found.")
    else:
        for p in profiles:
            click.echo(p)


@sync.command("delete")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--profile", required=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_delete(vault_path, profile, password):
    """Delete a profile from the vault."""
    try:
        delete_profile(Path(vault_path), password, profile)
        click.echo(f"Deleted profile '{profile}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
