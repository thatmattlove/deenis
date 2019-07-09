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
    elif click_input["config_file"]:
        config_path = Path().resolve(click_input["config_file"])
    if not click_input["ipv4"] and not click_input["ipv6"]:
        raise click.UsageError(
            click.style("At least one IP Address is required", fg="red", bold=True)
        )
    try:
        responses = Deenis(str(config_path)).AddHost(
            {
                "hostname": click_input["fqdn"],
                "ipv4": click_input["ipv4"],
                "ipv6": click_input["ipv6"],
            }
        )
        if responses:
            for res in responses:
                status, record_record, record, target, errors = res
                if status == "Success":
                    click.echo(
                        "Added "
                        + click.style(record_record, fg="green", bold=True)
                        + " Record for "
                        + click.style(record, fg="yellow", bold=True)
                        + " Pointing to "
                        + click.style(target, fg="blue", bold=True)
                    )
                elif status == "Failure":
                    click.echo(
                        "Error Adding "
                        + click.style(record_record, fg="magenta", bold=True)
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


@add_records.command("tenant", help="Bulk Add PTR Records for a Tenant/Customer")
@click.option("-c", "--config-file", "config_file", help="Path to YAML Config File")
@click.option(
    "-i", "--crm-id", "crm_id", default=None, help="Unique Tenant Indentifier"
)
@click.option(
    "-4", "--ipv4-prefix", "prefix4", default=None, help="IPv4 Prefix Assignment"
)
@click.option(
    "-6", "--ipv6-prefix", "prefix6", default=None, help="IPv6 Prefix Assignment"
)
@click.option(
    "-f4", "--ipv4-fqdn", "host4", default=None, help="FQDN for IPv4 PTR Target"
)
@click.option(
    "-f6", "--ipv6-fqdn", "host6", default=None, help="FQDN for IPv6 PTR Target"
)
def tenant_reverse(**click_input):
    """Add Tenant Records from CLI"""
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
    elif click_input["config_file"]:
        config_path = Path().resolve(click_input["config_file"])
    if not click_input["prefix4"] and not click_input["prefix6"]:
        raise click.UsageError(
            click.style("At least one prefix is required", fg="red", bold=True)
        )
    try:
        responses = Deenis(str(config_path)).TenantReverse(
            {
                "crm_id": click_input["crm_id"],
                "host4": click_input["host4"],
                "host6": click_input["host6"],
                "prefix4": click_input["prefix4"],
                "prefix6": click_input["prefix6"],
            }
        )
        """
        Response format:
        [
            (
                'Success',
                'A',
                'test011.omnificent.io',
                '199.34.95.250',
                []
            ),
            (
                'Success',
                'PTR',
                '250',
                'test011.omnificent.io',
                []
            )
        ]
        """
        nl = "\n"
        tab = "  "
        _text = {"fg": "white", "bold": True}
        _stat_suc = {"fg": "green", "bold": True}
        _stat_fail = {"fg": "red", "bold": True}
        _rec_type = {"fg": "yellow", "bold": True}
        _rec_name = {"fg": "magenta", "bold": True}
        _rec_trgt = {"fg": "cyan", "bold": True}
        _error = {"fg": "red"}
        click.secho(nl + "Records:" + nl, **_text)
        for res in responses:
            status, rec_type, rec_name, rec_trgt, errors = res
            if status == "Success":
                _status = ("⚡ " + status, _stat_suc)
            elif status == "Failure":
                _status = ("☝ " + status, _stat_fail)
            click.echo(
                tab
                + click.style(_status[0], **_status[1])
                + nl
                + tab * 4
                + click.style(rec_type, **_rec_type)
                + click.style(" ⟫ ", **_text)
                + click.style(rec_name, **_rec_name)
                + click.style(" ⟩ ", **_text)
                + click.style(rec_trgt, **_rec_trgt)
            )
            if errors:
                click.echo(tab * 4 + click.style("Errors: ", **_stat_fail))
                for err in errors:
                    if isinstance(err, dict):
                        for ename in err.keys():
                            click.echo(
                                tab * 6
                                + click.style(str(ename) + ":", **_error)
                                + tab
                                + click.style(str(err[ename]), **_error)
                            )
                    elif isinstance(err, str):
                        click.echo(tab * 4 + click.style(err, **_error))
    except (AttributeError, RuntimeError) as tenant_error:
        raise click.ClickException(tenant_error)


if __name__ == "__main__":
    add_records()
