"""CLI commands for exporting env profiles."""

import click
from pathlib import Path

from envoy_cli.vault import load_vault, vault_exists
from envoy_cli.export import export_env, SUPPORTED_FORMATS


@click.group()
def export():
    """Export env profiles to various formats."""
    pass


@export.command("profile")
@click.argument("profile_name")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--format", "fmt", default="shell", show_default=True, type=click.Choice(SUPPORTED_FORMATS), help="Output format.")
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
def cmd_export_profile(profile_name, vault_path, password, fmt, output):
    """Export a stored profile to the chosen format."""
    vault_path = Path(vault_path)
    if not vault_exists(vault_path):
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    vault = load_vault(vault_path, password)
    if profile_name not in vault:
        click.echo(f"Profile '{profile_name}' not found in vault.", err=True)
        raise SystemExit(1)

    env = vault[profile_name]
    result = export_env(env, fmt)

    if output:
        Path(output).write_text(result + "\n", encoding="utf-8")
        click.echo(f"Exported profile '{profile_name}' to '{output}' as {fmt}.")
    else:
        click.echo(result)
