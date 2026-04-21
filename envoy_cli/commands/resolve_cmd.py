"""CLI commands for resolving variable references in env profiles."""

import click
from envoy_cli.commands import sync
from envoy_cli.vault import load_vault, save_vault
from envoy_cli.resolve import resolve_env, list_unresolved, ResolveError


@click.group()
def resolve():
    """Resolve ${VAR} references within env profiles."""


@resolve.command("show")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--strict/--lenient", default=True, show_default=True,
              help="Fail on undefined references (strict) or leave them (lenient).")
def cmd_show_resolved(profile: str, vault_path: str, password: str, strict: bool):
    """Print the resolved env for PROFILE with all ${VAR} references expanded."""
    try:
        vault = load_vault(vault_path, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if profile not in vault:
        raise click.ClickException(f"Profile '{profile}' not found in vault.")

    raw_env: dict = vault[profile]
    try:
        resolved = resolve_env(raw_env, strict=strict)
    except ResolveError as exc:
        raise click.ClickException(str(exc))

    for key, value in sorted(resolved.items()):
        click.echo(f"{key}={value}")


@resolve.command("check")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_check_references(profile: str, vault_path: str, password: str):
    """List any unresolved ${VAR} references in PROFILE."""
    try:
        vault = load_vault(vault_path, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if profile not in vault:
        raise click.ClickException(f"Profile '{profile}' not found in vault.")

    raw_env: dict = vault[profile]
    unresolved = list_unresolved(raw_env)

    if not unresolved:
        click.echo(click.style("No unresolved references found.", fg="green"))
        return

    click.echo(click.style(f"{len(unresolved)} key(s) with unresolved references:", fg="yellow"))
    for key, refs in sorted(unresolved.items()):
        refs_str = ", ".join(f"${{{r}}}" for r in refs)
        click.echo(f"  {key}: {refs_str}")
