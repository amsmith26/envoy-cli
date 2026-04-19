"""CLI commands for linting .env files and vault profiles."""

import click
from envoy_cli.lint import lint_env, format_lint_results
from envoy_cli.file_handler import read_env_file
from envoy_cli.parser import parse_env_file
from envoy_cli.vault import load_vault, vault_exists
from envoy_cli.crypto import decrypt_env


@click.group()
def lint():
    """Lint .env files for common issues."""


@lint.command("file")
@click.argument("env_file", default=".env")
def cmd_lint_file(env_file: str):
    """Lint a local .env file."""
    try:
        raw = read_env_file(env_file)
    except FileNotFoundError:
        click.echo(f"File not found: {env_file}", err=True)
        raise SystemExit(1)

    raw_lines = raw.splitlines()
    env = parse_env_file(raw)
    issues = lint_env(env, raw_lines)
    click.echo(f"Linting {env_file}...")
    click.echo(format_lint_results(issues))
    if issues:
        raise SystemExit(1)


@lint.command("profile")
@click.argument("profile")
@click.option("--vault", "vault_file", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_lint_profile(profile: str, vault_file: str, password: str):
    """Lint a profile stored in the vault."""
    if not vault_exists(vault_file):
        click.echo("Vault not found.", err=True)
        raise SystemExit(1)

    try:
        vault = load_vault(vault_file, password)
    except Exception:
        click.echo("Failed to load vault. Wrong password?", err=True)
        raise SystemExit(1)

    if profile not in vault:
        click.echo(f"Profile '{profile}' not found in vault.", err=True)
        raise SystemExit(1)

    env = vault[profile]
    issues = lint_env(env)
    click.echo(f"Linting profile '{profile}'...")
    click.echo(format_lint_results(issues))
    if issues:
        raise SystemExit(1)
