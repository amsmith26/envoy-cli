"""CLI commands for schema validation."""
import click
from envoy_cli.commands import pass_workspace
from envoy_cli.schema import load_schema, validate_env, SchemaValidationError
from envoy_cli.vault import load_vault, vault_exists
from envoy_cli.file_handler import read_env_file
from envoy_cli.parser import parse_env_file


@click.group()
def schema():
    """Validate env profiles against a schema."""


@schema.command("validate-profile")
@click.argument("profile")
@click.argument("schema_file")
@click.option("--password", prompt=True, hide_input=True)
@pass_workspace
def cmd_validate_profile(workspace: str, profile: str, schema_file: str, password: str):
    """Validate a vault profile against a schema file."""
    if not vault_exists(workspace):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    try:
        schema = load_schema(schema_file)
        vault = load_vault(workspace, password)
        if profile not in vault:
            click.echo(f"Profile '{profile}' not found.", err=True)
            raise SystemExit(1)
        errors = validate_env(vault[profile], schema)
        if errors:
            for e in errors:
                click.echo(f"  ✗ {e}")
            raise SystemExit(1)
        click.echo(f"✓ Profile '{profile}' is valid.")
    except SchemaValidationError as exc:
        for e in exc.errors:
            click.echo(f"  ✗ {e}")
        raise SystemExit(1)


@schema.command("validate-file")
@click.argument("env_file")
@click.argument("schema_file")
@pass_workspace
def cmd_validate_file(workspace: str, env_file: str, schema_file: str):
    """Validate a .env file against a schema file."""
    try:
        raw = read_env_file(env_file)
        env = parse_env_file(raw)
        schema = load_schema(schema_file)
        errors = validate_env(env, schema)
        if errors:
            for e in errors:
                click.echo(f"  ✗ {e}")
            raise SystemExit(1)
        click.echo(f"✓ '{env_file}' is valid.")
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
