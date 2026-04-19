"""CLI commands for template rendering."""
from __future__ import annotations
import click
from envoy_cli.vault import load_vault, vault_exists
from envoy_cli.template import render_file, render_template, collect_placeholders


@click.group()
def template() -> None:
    """Render templates using env profiles."""


@template.command("render")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--vault", "vault_file", required=True, type=click.Path(), help="Vault file path")
@click.option("--profile", required=True, help="Profile name to use")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output file (default: stdout)")
@click.option("--strict", is_flag=True, default=False, help="Error on missing placeholders")
def cmd_render(template_file: str, vault_file: str, profile: str, password: str, output: str | None, strict: bool) -> None:
    """Render TEMPLATE_FILE substituting values from PROFILE."""
    if not vault_exists(vault_file):
        click.echo(f"Vault not found: {vault_file}", err=True)
        raise SystemExit(1)

    vault = load_vault(vault_file, password)
    if profile not in vault:
        click.echo(f"Profile '{profile}' not found in vault.", err=True)
        raise SystemExit(1)

    env = vault[profile]
    try:
        result = render_file(template_file, env, strict=strict)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(result)
        click.echo(f"Rendered to {output}")
    else:
        click.echo(result, nl=False)


@template.command("inspect")
@click.argument("template_file", type=click.Path(exists=True))
def cmd_inspect(template_file: str) -> None:
    """List all placeholder keys found in TEMPLATE_FILE."""
    with open(template_file, "r", encoding="utf-8") as fh:
        content = fh.read()
    keys = collect_placeholders(content)
    if not keys:
        click.echo("No placeholders found.")
    else:
        for key in keys:
            click.echo(key)
