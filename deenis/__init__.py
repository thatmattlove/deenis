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
        self.providers = [p for p in self.conf["provider"]]
        self.zones = [z for z in self.conf["zone"]]
        self.zp_map = {}
        for p in self.providers:
            self.zp_map[p] = []
            for z in self.zones:
                if p in self.conf["zone"][z]["providers"]:
                    self.zp_map[p].append(z)

    def AddHost(self, input_params):
        """Attempts to add a "single" host record. For a given FQDN, will add A, AAAA, and 2 PTR \
        records."""
        records = construct.records(**input_params)
        zones = [a for b in [r.keys() for r in records] for a in b]
        response = None
        for zone in zones:
            if not self.conf["zone"].get(zone, None):
                raise AttributeError("Zone {} is not defined".format(zone))
            zone_providers = self.conf["zone"][zone].get("providers")
            for provider in zone_providers:
                zone_map = self.zp_map.get(provider)
                provider_conf = self.conf["provider"].get(provider, None)
                if not provider_conf:
                    raise AttributeError("Provider {} is not defined".format(provider))
                filtered_records = []
                for r in records:
                    for z in r.keys():
                        if z in zone_map:
                            filtered_records.append({z: r[z]})
                            response = getattr(
                                call.Provider(filtered_records), provider
                            )(provider_conf)
        return response
