"""Shared decorators and utilities for envoy-cli commands."""

import click


def vault_options(func):
    """Decorator that adds --vault and --password options to a command."""
    func = click.option(
        "--vault",
        default=".env.vault",
        show_default=True,
        help="Path to the vault file.",
    )(func)
    func = click.option(
        "--password",
        prompt=True,
        hide_input=True,
        help="Vault password.",
    )(func)
    return func
