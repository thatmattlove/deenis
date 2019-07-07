#!/usr/bin/env python3
"""
CLI for Accessing Deenis
"""
# Standard Imports
import sys
from pathlib import Path

# Module Imports
import click

# Path Fixes
working_dir = Path(__file__).resolve().parent
sys.path.append(str(working_dir))
# Project Imports
from deenis import Deenis


@click.group(
    help=(
        "Deenis can be used to group and automate boring DNS tasks. For example, "
        "`host` can take a hostname, IPv4 Address, and IPv6 Address, and create "
        "forward A & AAAA, and reverse PTR records (4 actions) with a single command."
    )
)
def add_records():
    """Click Command Group Definition"""
    # pylint: disable=unnecessary-pass
    # Dear Pylint: This is how Click likes to do things. Get over it bruh.
    pass


@add_records.command("host", help="Add a Host Record")
@click.option("-c", "--config-file", "config_file", help="Path to YAML Config File")
@click.option("-4", "--ipv4-address", "ipv4", default=None, help="IPv4 Address")
@click.option("-6", "--ipv6-address", "ipv6", default=None, help="IPv6 Address")
@click.option("-f", "--fqdn", "fqdn", required=True, help="FQDN")
def host(**click_input):
    """Add host records from CLI"""
    if not click_input["config_file"]:
        config_path = Path.cwd().joinpath("deenis.yaml")
        if not config_path.exists():
            raise click.UsageError(
                click.style(
                    (
                        f"Config file not specified and not found at {config_path}. "
                        "Please specify a config file path."
                    ),
                    fg="red",
                    bold=True,
                )
            )
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
                status, record_type, record, target, errors = res
                if status == "Success":
                    click.echo(
                        "Added "
                        + click.style(record_type, fg="green", bold=True)
                        + " Record for "
                        + click.style(record, fg="yellow", bold=True)
                        + " Pointing to "
                        + click.style(target, fg="blue", bold=True)
                    )
                elif status == "Failure":
                    click.echo(
                        "Error Adding "
                        + click.style(record_type, fg="magenta", bold=True)
                        + " Record for "
                        + click.style(record, fg="cyan", bold=True)
                        + " Pointing to "
                        + click.style(target, fg="red", bold=True)
                        + f"\nErrors:\n"
                    )
                    for err in errors:
                        click.secho(err, fg="red")
        if not responses:
            click.secho("\nNo records were added", fg="magenta", bold=True)
    except (RuntimeError, AttributeError) as error_exception:
        raise click.UsageError(click.style(str(error_exception), fg="red", bold=True))


if __name__ == "__main__":
    add_records()
