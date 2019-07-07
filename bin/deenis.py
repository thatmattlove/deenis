#!/usr/bin/env python3
"""
CLI for Accessing Deenis
"""
# Standard Imports
import sys

# Module Imports
import click

# Project Imports
sys.path.append(".")
from deenis import Deenis


@click.group(
    help=(
        "Deenis can be used to group and automate boring DNS tasks. For example, `host` can take "
        "a hostname, IPv4 Address, and IPv6 Address, and create forward A & AAAA, and reverse "
        "PTR records (4 actions) with a single command."
    )
)
def add_records():
    """Click Command Group Definition"""
    # pylint: disable=unnecessary-pass
    # Dear Pylint: This is how Click likes to do things. Get over it bruh.
    pass


@add_records.command("host", help="Add a Host Record")
@click.option(
    "-c", "--config-file", "config_file", required=True, help="Path to TOML Config File"
)
@click.option("-4", "--ipv4-address", "ipv4", default=None, help="IPv4 Address")
@click.option("-6", "--ipv6-address", "ipv6", default=None, help="IPv6 Address")
@click.option("-f", "--fqdn", "fqdn", required=True, help="FQDN")
def host(**click_input):
    """Add host records from CLI"""
    if not click_input["ipv4"] and not click_input["ipv6"]:
        raise click.UsageError(
            click.style("At least one IP Address is required", fg="red", bold=True)
        )
    try:
        responses = Deenis(click_input["config_file"]).AddHost(
            {
                "hostname": click_input["fqdn"],
                "ipv4": click_input["ipv4"],
                "ipv6": click_input["ipv6"],
            }
        )
        if responses:
            for res in responses:
                if res[0] in (200,):
                    click.echo(
                        click.style(
                            f"Successfully added: {res[1]}", fg="green", bold=True
                        )
                    )
                elif res[0] in (401, 403, 405, 415, 429):
                    click.echo(
                        click.style(f"Error adding: {res[1]}", fg="magenta", bold=True)
                        + click.style(f"Errors: {res[2]}", fg="magenta")
                    )
        if not responses:
            click.secho("\nNo records were added", fg="magenta", bold=True)
    except (RuntimeError, AttributeError) as error_exception:
        raise click.UsageError(click.style(str(error_exception), fg="red", bold=True))


if __name__ == "__main__":
    add_records()
