import click
from envoy_cli.commands import cli
from envoy_cli.snapshot import list_snapshots, create_snapshot, restore_snapshot, delete_snapshot


@cli.group()
def snapshot():
    """Manage environment snapshots."""
    pass


@snapshot.command("create")
@click.argument("profile")
@click.option("--vault", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--label", default=None, help="Optional snapshot label")
def cmd_create_snapshot(profile, vault, password, label):
    """Create a snapshot of a profile."""
    try:
        name = create_snapshot(vault, password, profile, label=label)
        click.echo(f"Snapshot created: {name}")
    except KeyError:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot.command("list")
@click.argument("profile")
@click.option("--vault", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_list_snapshots(profile, vault, password):
    """List snapshots for a profile."""
    try:
        snaps = list_snapshots(vault, password, profile)
        if not snaps:
            click.echo(f"No snapshots for profile '{profile}'.")
        for s in snaps:
            click.echo(s)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot.command("restore")
@click.argument("profile")
@click.argument("label")
@click.option("--vault", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_restore_snapshot(profile, label, vault, password):
    """Restore a profile from a snapshot."""
    try:
        restore_snapshot(vault, password, profile, label)
        click.echo(f"Profile '{profile}' restored from snapshot '{label}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot.command("delete")
@click.argument("profile")
@click.argument("label")
@click.option("--vault", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_delete_snapshot(profile, label, vault, password):
    """Delete a snapshot."""
    try:
        delete_snapshot(vault, password, profile, label)
        click.echo(f"Snapshot '{label}' deleted from profile '{profile}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
