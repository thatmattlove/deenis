#!/usr/bin/env python3
"""
CLI for Accessing Deenis
"""
# Module Imports
import click

# Project Imports
from deenis import execute


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
@click.option("-4", "--ipv4", "ipv4", default=None, help="IPv4 Address")
@click.option("-6", "--ipv6", "ipv6", default=None, help="IPv6 Address")
@click.option("-f", "--fqdn", "fqdn", required=True, help="FQDN")
def host(ipv4, ipv6, fqdn):
    """Add host records from CLI"""
    try:
        responses = execute.host(ipv4, ipv6, fqdn)
        if responses:
            for res in responses:
                if res["success"]:
                    click.echo(click.style(f'{res["message"]}', fg="green", bold=True))
                if not res["success"]:
                    click.echo(
                        click.style(f'{res["message"]}', fg="magenta", bold=True)
                    )
        if not responses:
            click.secho("\nNo records were added", fg="magenta", bold=True)
    except RuntimeError as runtime_error:
        click.secho("\n" + runtime_error, fg="red", bold=True)


if __name__ == "__main__":
    add_records()
