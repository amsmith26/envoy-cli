"""CLI commands for diffing .env profiles or files."""

import click
from envoy_cli.vault import load_vault, vault_exists
from envoy_cli.diff import diff_envs, format_diff, has_changes
from envoy_cli.file_handler import read_env_file
from envoy_cli.parser import parse_env_file


@click.group()
def diff():
    """Diff .env files or vault profiles."""
    pass


@diff.command("profiles")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--vault", "vault_file", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_diff_profiles(profile_a: str, profile_b: str, vault_file: str, password: str):
    """Diff two profiles stored in the vault."""
    if not vault_exists(vault_file):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)

    vault = load_vault(vault_file, password)

    if profile_a not in vault:
        click.echo(f"Profile '{profile_a}' not found.", err=True)
        raise SystemExit(1)
    if profile_b not in vault:
        click.echo(f"Profile '{profile_b}' not found.", err=True)
        raise SystemExit(1)

    result = diff_envs(vault[profile_a], vault[profile_b])
    lines = format_diff(result)

    if not lines:
        click.echo("No differences found.")
    else:
        click.echo(f"Diff: {profile_a} -> {profile_b}")
        for line in lines:
            click.echo(line)


@diff.command("file")
@click.argument("profile")
@click.option("--env-file", "env_file", default=".env", show_default=True)
@click.option("--vault", "vault_file", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_diff_file(profile: str, env_file: str, vault_file: str, password: str):
    """Diff a local .env file against a vault profile."""
    if not vault_exists(vault_file):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)

    vault = load_vault(vault_file, password)

    if profile not in vault:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)

    local_env = parse_env_file(read_env_file(env_file))
    result = diff_envs(vault[profile], local_env)
    lines = format_diff(result)

    if not lines:
        click.echo("No differences found.")
    else:
        click.echo(f"Diff: {profile} (vault) -> {env_file} (local)")
        for line in lines:
            click.echo(line)
