"""
Deenis is a tool used to consolidate and automate boring DNS tasks
"""
__all__ = ["Deenis"]
__version__ = "0.0.1"

# Standard Imports
import os

# Project Imports
from deenis import call
from deenis import construct

from logzero import logger


class Deenis:
    """Main Deenis class - initializes with config parameters from file or dictionary input"""

    # pylint: disable=invalid-name,too-few-public-methods
    # Allowing PascalCase for public methods

    def __init__(self, config_params=None):
        self.config_params = config_params
        if not self.config_params:
            raise ValueError(
                "A TOML config file or a parameters dictionary must be specified"
            )
        if isinstance(self.config_params, dict):
            self.conf = self.config_params
        elif isinstance(self.config_params, str):
            if not os.path.exists(self.config_params):
                raise FileNotFoundError(
                    "Config file {} not found.".format(self.config_params)
                )
            if os.path.exists(self.config_params):
                import toml

                self.conf = toml.load(self.config_params)
        self.providers = [provider for provider in self.conf["provider"]]
        self.zones = [zone for zone in self.conf["zone"]]
        self.zp_map = {}
        for provider in self.providers:
            self.zp_map[provider] = []
            for zone in self.zones:
                if provider in self.conf["zone"][zone]["providers"]:
                    self.zp_map[provider].append(zone)

    def AddHost(self, input_params):
        """Attempts to add a "single" host record. For a given FQDN, will add A, AAAA, and 2 PTR \
        records."""
        records = construct.records(**input_params)
        response = None
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
        for provider in add_map.keys():
            response_class = getattr(call, provider)
            response = response_class(add_map[provider][0]).add_record(
                add_map[provider][1]
            )
            return response
