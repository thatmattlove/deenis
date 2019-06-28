"""
Defines and Executes Actions Per-Provider
"""
import json
import requests


class Cloudflare:
    """Cloudflare-specific functions"""

    # pylint: disable=too-few-public-methods
    # Dear Pylint: Sometimes, one must make one's code scalable for future additions. This is one
    #              of those times.

    def __init__(self, provider_conf):
        self.api = provider_conf["api"]
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
        return output


class Handle:
    """Per-provider API call handlers"""

    # pylint: disable=too-few-public-methods
    # Dear Pylint: Sometimes, one must make one's code scalable for future additions. This is one
    #              of those times.
    def __init__(self, records):
        self.records = records

    def cloudflare(self, provider_conf):
        """Initializes Cloudflare-specific actions"""
        output = []
        for params in self.records:
            response = Cloudflare(provider_conf).add_record(params)
            output.append(response)
        return output
