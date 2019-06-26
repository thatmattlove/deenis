"""
Performs Input Validation, Record Construction, & API Calls
"""
# Standard Imports
import json
import logging
import ipaddress

# Module Imports
import requests
import logzero
from logzero import logger

# Project Imports
from deenis import config

# Logzero Configuration
if config.debug_state():
    logzero.loglevel(logging.DEBUG)
elif not config.debug_state():
    logzero.loglevel(logging.INFO)


class Construct:
    """Constructs usable data structures for use by APIs"""

    def __init__(self, hostname=None):
        self.hostname = hostname

    def forward(self):
        """Deconstructs FQDN and returns dict of elements"""
        hosts = self.hostname.split(".")
        domains = hosts[-2:]
        host = hosts[0:-2:]
        host_attr = {}
        host_attr["fqdn"] = self.hostname
        host_attr["domain"] = f"{domains[0]}.{domains[1]}"
        host_attr["host"] = ".".join(host)
        return host_attr

    def ip_addr(self, ipv4, ipv6):
        """Validates IP addresses and returns list of A, AAAA, and PTR records to add"""
        z_forward = self.forward()
        records = []
        if ipv4:
            try:
                ipv4 = ipaddress.ip_address(ipv4)
                z_reverse4_full = (
                    ipaddress.ip_network(ipv4)
                    .supernet(new_prefix=24)
                    .network_address.reverse_pointer
                )
                z_reverse4 = ".".join(z_reverse4_full.split(".")[1:])
                #
                forward_4 = {
                    z_forward["domain"]: {
                        "type": "A",
                        "name": z_forward["fqdn"],
                        "content": str(ipv4),
                    }
                }
                records.append(forward_4)
                reverse_4 = {
                    z_reverse4: {
                        "type": "PTR",
                        "name": str(ipv4).split(".")[3],
                        "content": self.hostname,
                    }
                }
                records.append(reverse_4)
            except ValueError:
                raise AttributeError(f"{ipv4} is an invalid IPv4 Address")
        if ipv6:
            try:
                ipv6 = ipaddress.ip_address(ipv6)
                z_reverse_list = str(ipv6.reverse_pointer).split(".")
                z_reverse6 = ".".join(z_reverse_list[-10:])
                z_reverse6_host = ".".join(z_reverse_list[0:-10:])
                #
                forward_6 = {
                    z_forward["domain"]: {
                        "type": "AAAA",
                        "name": z_forward["fqdn"],
                        "content": str(ipv6),
                    }
                }
                records.append(forward_6)
                #
                reverse_6 = {
                    z_reverse6: {
                        "type": "PTR",
                        "name": z_reverse6_host,
                        "content": self.hostname,
                    }
                }
                records.append(reverse_6)
            except ValueError:
                raise AttributeError(f"{ipv6} is an invalid IPv6 Address")
        return records


class Cloudflare:
    """Cloudflare-specific functions"""

    def __init__(self):
        self.api = config.api("cloudflare")
        self.url = self.api["baseurl"]
        self.headers = {
            "Content-Type": "application/json",
            "X-Auth-Key": self.api["key"],
            "X-Auth-Email": self.api["email"],
        }

    def get_zone_id(self, zone):
        """Gets Cloudflare zone_id by querying the list of zones endpoint, filtered by the zone \
        name being queried"""
        endpoint = self.url + "zones/"
        params = {"name": zone}
        res_raw = requests.get(url=endpoint, headers=self.headers, params=params)
        res_dict = json.loads(json.dumps(res_raw.json()))
        zone_id = None
        if res_dict["result"]:
            zone_id = res_dict["result"][0]["id"]
        if not res_dict["result"]:
            msg = "Zone Lookup Failed for {}".format(zone)
            raise AttributeError(msg)
        return zone_id

    def add_record(self, input_params):
        """Adds Cloudflare DNS record"""
        logger.debug(f"Add Record: {input_params}")
        zone = [z for z in input_params][0]
        record_params = input_params[zone]
        try:
            zone_id = self.get_zone_id(zone)
        except AttributeError as zone_error:
            raise RuntimeError(zone_error)
        endpoint = self.url + "zones/" + zone_id + "/dns_records"
        params = {
            "type": record_params["type"],
            "name": record_params["name"],
            "content": record_params["content"],
            "ttl": record_params.get("ttl", 1),
            "proxied": record_params.get("proxied", False),
        }
        res_raw = requests.post(
            url=endpoint, headers=self.headers, data=json.dumps(params)
        )
        res_dict = json.loads(json.dumps(res_raw.json()))
        output = None
        if res_dict["success"]:
            output = {
                "success": res_dict["success"],
                "message": (
                    f'Added {res_dict["result"]["type"]} Record for '
                    f'{res_dict["result"]["name"]}, pointing to {res_dict["result"]["content"]}'
                ),
            }
        if not res_dict["success"]:
            output = {
                "success": res_dict["success"],
                "message": (
                    f'Error while adding {record_params["type"]} Record for '
                    f'{record_params["name"]}, pointing to {record_params["content"]}: '
                    f'{res_dict["errors"][0]["message"]}'
                ),
            }
        logger.debug(f"Dict Response: {res_dict}")
        return output


class Provider:
    """Per-provider API call handlers"""

    # pylint: disable=too-few-public-methods
    # Dear Pylint: Sometimes, one must make one's code scalable for future additions. This is one
    #              of those times.
    def __init__(self, records):
        self.records = records

    def cloudflare(self):
        """Initializes Cloudflare-specific actions"""
        output = []
        for params in self.records:
            response = Cloudflare().add_record(params)
            output.append(response)
        logger.debug(f"Output List: {output}")
        return output


class Write:
    """Entry point for API calls"""

    # pylint: disable=too-few-public-methods
    # Dear Pylint: Sometimes, one must make one's code scalable for future additions. This is one
    #              of those times.
    def __init__(self, provider, target):
        """
        Target Params:
        {
            "hostname": "test.omnificent.io",
            "ipv4": "192.0.2.1",
            "ipv6": "2001:db8::1",
            "crm": "19000",
        }
        """
        self.provider = provider
        self.target = target

    def add(self):
        """Provider-agnostic function to add records"""
        hostname = self.target.get("hostname", None)
        ipv4 = self.target.get("ipv4", None)
        ipv6 = self.target.get("ipv6", None)
        try:
            records = Construct(hostname).ip_addr(ipv4, ipv6)
        except AttributeError as ip_error:
            raise RuntimeError(ip_error)
        response = getattr(Provider(records), self.provider)()
        return response
