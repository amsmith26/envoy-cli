"""Register the access command group with the main CLI.

This shim exists so that main.py can import a single symbol per command
module without needing to know the internal group name.

Usage in envoy_cli/commands/main.py::

    from envoy_cli.commands.access_cmd_register import register
    register(cli)
"""

from __future__ import annotations

import click

from envoy_cli.commands.access_cmd import access


def register(cli: click.Group) -> None:
    """Attach the *access* command group to *cli*."""
    cli.add_command(access)
