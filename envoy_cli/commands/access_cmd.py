"""CLI commands for managing profile access control."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_access import AccessError, check_access, get_access, grant_access, revoke_access


@click.group()
def access() -> None:
    """Manage read/write access for profiles."""


@access.command("grant")
@vault_options
@click.argument("profile")
@click.argument("principal")
@click.option("--role", type=click.Choice(["read", "write"]), required=True, help="Role to grant.")
def cmd_grant_access(vault: str, password: str, profile: str, principal: str, role: str) -> None:
    """Grant PRINCIPAL the ROLE on PROFILE."""
    try:
        record = grant_access(vault, password, profile, principal, role)
        click.echo(f"Granted '{role}' to '{principal}' on profile '{profile}'.")
        click.echo(f"  readers: {record['readers']}")
        click.echo(f"  writers: {record['writers']}")
    except AccessError as exc:
        raise click.ClickException(str(exc)) from exc


@access.command("revoke")
@vault_options
@click.argument("profile")
@click.argument("principal")
@click.option("--role", type=click.Choice(["read", "write"]), required=True, help="Role to revoke.")
def cmd_revoke_access(vault: str, password: str, profile: str, principal: str, role: str) -> None:
    """Revoke PRINCIPAL's ROLE on PROFILE."""
    try:
        record = revoke_access(vault, password, profile, principal, role)
        click.echo(f"Revoked '{role}' from '{principal}' on profile '{profile}'.")
        click.echo(f"  readers: {record['readers']}")
        click.echo(f"  writers: {record['writers']}")
    except AccessError as exc:
        raise click.ClickException(str(exc)) from exc


@access.command("show")
@vault_options
@click.argument("profile")
def cmd_show_access(vault: str, password: str, profile: str) -> None:
    """Show the access list for PROFILE."""
    try:
        record = get_access(vault, password, profile)
        click.echo(f"Profile: {profile}")
        click.echo(f"  readers: {record['readers'] or '(none)'}")
        click.echo(f"  writers: {record['writers'] or '(none)'}")
    except AccessError as exc:
        raise click.ClickException(str(exc)) from exc


@access.command("check")
@vault_options
@click.argument("profile")
@click.argument("principal")
@click.option("--role", type=click.Choice(["read", "write"]), required=True)
def cmd_check_access(vault: str, password: str, profile: str, principal: str, role: str) -> None:
    """Check whether PRINCIPAL has ROLE on PROFILE."""
    try:
        allowed = check_access(vault, password, profile, principal, role)
        status = "ALLOWED" if allowed else "DENIED"
        click.echo(f"{principal} {status} {role} on {profile}")
    except AccessError as exc:
        raise click.ClickException(str(exc)) from exc
