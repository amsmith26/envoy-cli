import click
from envoy_cli.commands import sync
from envoy_cli.import_env import import_env
from envoy_cli.sync import push_env
from envoy_cli.audit import record_event


@sync.command("import")
@click.argument("profile")
@click.argument("source")
@click.option("--format", "fmt", type=click.Choice(["dotenv", "shell", "json"]), default="dotenv", show_default=True)
@click.option("--keys", default=None, help="Comma-separated list of keys to import")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--vault", default=".env.vault", show_default=True, help="Path to vault file")
def cmd_import_profile(profile, source, fmt, keys, password, vault):
    """Import env vars from a file into a vault profile."""
    filter_keys = [k.strip() for k in keys.split(",")] if keys else None

    try:
        if source == "-":
            content = click.get_text_stream("stdin").read()
            env = import_env(content, fmt=fmt, keys=filter_keys, from_shell=False)
        else:
            with open(source, "r") as f:
                content = f.read()
            env = import_env(content, fmt=fmt, keys=filter_keys, from_shell=(fmt == "shell"))
    except FileNotFoundError:
        click.echo(f"Error: source file '{source}' not found.", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error reading source: {e}", err=True)
        raise click.Abort()

    try:
        push_env(vault, profile, env, password)
        record_event(vault, "import", profile, list(env.keys()))
        click.echo(f"Imported {len(env)} key(s) into profile '{profile}'.")
    except Exception as e:
        click.echo(f"Error saving to vault: {e}", err=True)
        raise click.Abort()
