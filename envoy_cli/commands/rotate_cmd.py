"""CLI commands for vault password rotation."""

import click
from envoy_cli.rotate import rotate_vault_password


@click.group()
def rotate():
    """Rotate the master password for a vault."""


@rotate.command("run")
@click.argument("vault_file")
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current vault password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
def cmd_rotate(vault_file: str, old_password: str, new_password: str) -> None:
    """Re-encrypt VAULT_FILE with a new master password."""
    try:
        profiles = rotate_vault_password(vault_file, old_password, new_password)
        click.echo(
            f"Rotated {len(profiles)} profile(s): {', '.join(profiles) or 'none'}"
        )
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception:
        click.echo("Error: wrong password or corrupted vault.", err=True)
        raise SystemExit(1)
