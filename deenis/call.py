"""
Defines and Executes Actions Per-Provider
"""

# Standard Imports
import json

# Module Imports
import requests
import diskcache

from logzero import logger

cache = diskcache.Cache("/tmp/deenis")


class cloudflare:
    """Cloudflare-specific functions"""

    # pylint: disable=too-few-public-methods
    # Dear Pylint: Sometimes, one must make one's code scalable for future additions. This is one
    #              of those times.

    def __init__(self, provider_conf):
        self.api = provider_conf["api"]
        self.url = self.api["baseurl"]

    def provider_session(self):
        """Reusable sesssion for all functions"""
        provider_headers = {
            "Content-Type": "application/json",
            "X-Auth-Key": self.api["key"],
            "X-Auth-Email": self.api["email"],
        }
        session = requests.Session()
        session.headers.update(provider_headers)
        return session

    def get_zone_id(self, zone):
        """Gets Cloudflare zone_id by querying the list of zones endpoint, filtered by the zone \
        name being queried"""
        zone_id = cache.get(zone)
        logger.debug(f"Pre-Run Zone ID: {zone_id}")
        if not zone_id:
            try:
                endpoint = self.url + "zones/"
                params = {"name": zone}
                with self.provider_session().get(endpoint, params=params) as res_raw:
                    res_json = res_raw.json()
                    if res_raw.status_code in (401, 403, 405, 415, 429):
                        # For HTTP responses that would indicate a code-level issue, raise exception
                        raise RuntimeError(
                            (
                                res_raw.status_code,
                                *tuple(params.values()),
                                res_json["errors"],
                            )
                        )
                    if res_json["result"]:
                        cache.add(zone, res_json["result"][0]["id"])
                        zone_id = cache.get(zone)
                    if not res_json["result"]:
                        raise AttributeError(f"Zone Lookup Failed for {zone}")
            except requests.exceptions.RequestException as req_exception:
                raise RuntimeError(req_exception)
        return zone_id

    def add_record(self, targets):
        """Adds Cloudflare DNS record"""
        output = []
        for target in targets:
            zone_name = [zone for zone in target.keys()][0]
            zone_id = self.get_zone_id(zone_name)
            if not zone_id:
                raise RuntimeError(f"Zone {zone_name} does not have an Zone ID")
            target[zone_id] = target.pop(zone_name)
        for target in targets:
            target_id = [id for id in target.keys()][0]
            target_params = [
                params for params in [target.get(zone) for zone in target]
            ][0]
            if not target_params:
                raise RuntimeError(
                    f"Error: Target Params for {zone} are {target_params}"
                )
            provider_params = {
                "type": target_params["type"],
                "name": target_params["name"],
                "content": target_params["content"],
                "ttl": target_params.get("ttl", 1),
                "proxied": target_params.get("proxied", False),
            }
            endpoint = "".join([self.url, "zones/", target_id, "/dns_records"])
            try:
                with self.provider_session().post(
                    endpoint, data=json.dumps(provider_params)
                ) as res_raw:
                    res_json = res_raw.json()
                    if res_raw.status_code in (401, 403, 405, 415, 429):
                        # For HTTP responses that would indicate a code-level issue, raise exception
                        raise RuntimeError(
                            (
                                res_raw.status_code,
                                *tuple(provider_params.values())[0:3],
                                res_json["errors"],
                            )
                        )
                    output.append(
                        (
                            res_raw.status_code,
                            *tuple(provider_params.values())[0:3],
                            res_json["errors"],
                        )
                    )
            except requests.exceptions.RequestException as req_exception:
                self.provider_session().close()
                raise RuntimeError(req_exception)
        self.provider_session().close()
        return output
