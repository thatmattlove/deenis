"""
Deenis is a tool used to consolidate and automate boring DNS tasks
"""
__all__ = ["Deenis"]
__version__ = "0.0.1"

# Standard Imports
import os
from pathlib import Path

# Project Imports
from deenis import call
from deenis import construct


class Deenis:
    """
    Main Deenis class - initializes with config parameters from file or
    dictionary input.
    """

    # pylint: disable=invalid-name,too-few-public-methods
    # Allowing PascalCase for public methods

    def __init__(self, config_params=None):
        self.config_params = config_params
        if not self.config_params:
            raise ValueError(
                "A YAML config file or a parameters dictionary must be specified"
            )
        if isinstance(self.config_params, dict):
            self.conf = self.config_params
        elif isinstance(self.config_params, str):
            config_path = Path(config_params).resolve()
            if not config_path.exists():
                raise FileNotFoundError("Config file {} not found.".format(config_path))

            import yaml

            with open(config_path) as config_yaml:
                self.conf = yaml.safe_load(config_yaml)
        self.providers = [provider for provider in self.conf["provider"]]
        self.zones = [zone for zone in self.conf["zone"]]
        self.zp_map = {}
        for provider in self.providers:
            self.zp_map[provider] = []
            for zone in self.zones:
                if provider in self.conf["zone"][zone]["providers"]:
                    self.zp_map[provider].append(zone)

    def map_zones(self, records):
        """
        Maps input record data to configured providers and zones.

        Returns dict of provider configs and zone mappings specific to
        the input records.
        """
        add_map = {}
        filtered_records = []
        for record in records:
            zone_name = [zone for zone in record.keys()][0]
            if not self.conf["zone"].get(zone_name, None):
                raise AttributeError("Zone {} is not defined".format(zone_name))
            zone_providers = self.conf["zone"][zone_name].get("providers")
            for provider in zone_providers:
                provider_zones = self.zp_map.get(provider)
                provider_conf = self.conf["provider"].get(provider, None)
                if not provider_conf:
                    raise AttributeError("Provider {} is not defined".format(provider))
                if zone_name in provider_zones:
                    filtered_records.append({zone_name: record[zone_name]})
                add_map[provider] = (provider_conf, filtered_records)
        return add_map

    def AddHost(self, input_params):
        """
        Attempts to add a "single" host record. For a given FQDN, will
        add A, AAAA, and 2 PTR records.
        """
        records = construct.host_records(**input_params)
        add_map = self.map_zones(records)
        for provider, params in add_map.items():
            response_class = getattr(call, provider)
            provider_response = response_class(params[0]).add_record(params[1])
            return provider_response

    def TenantReverse(self, input_params):
        """
        Input Format:
        {
            "crm_id": 12345,
            "host4": "ip4.example.com",
            "host6": "ip6.example.com",
            "prefix4": "192.0.2.0/28",
            "prefix6": "2001:db8::/48"
        }
        """
        if input_params["crm_id"] and isinstance(input_params["crm_id"], int):
            input_params["crm_id"] = str(input_params["crm_id"])
        records = construct.tenant_records(**input_params)
        add_map = self.map_zones(records)
        for provider, params in add_map.items():
            response_class = getattr(call, provider)
            provider_response = response_class(params[0]).add_record(params[1])
            return provider_response
