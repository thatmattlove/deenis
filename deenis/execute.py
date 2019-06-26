"""
Main Deenis Front End
"""

# Project Imports
import call


def host(ipv4, ipv6, fqdn):
    """Attempts to add a "single" host record. For a given FQDN, will add \
    A, AAAA, and 2 PTR records."""
    # Build dict to send to call module, initialize
    to_add = {"ipv4": ipv4, "ipv6": ipv6, "hostname": fqdn}
    # Currently hardcoded to Cloudflare
    write = call.Write("cloudflare", to_add)
    try:
        adds = write.add()
        # Return will be a list of dicts, or an empty list
        return adds
    except RuntimeError as runtime_error:
        raise RuntimeError(runtime_error)
