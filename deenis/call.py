"""
Performs Input Validation, Record Construction, & API Calls
"""

from deenis import providers


class Provider:
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
            response = providers.Cloudflare(provider_conf).add_record(params)
            output.append(response)
        return output
