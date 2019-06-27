"""
Constructs Usable Data Structures for use by APIs
"""
# Module Imports
import ipaddress


def records(**kwargs):
    """Builds list of nested dicts where each parent key is the zone, and each zone's child dict \
    contains a k/v of DNS record type (A, AAAA, PTR, etc.), DNS record name, and DNS record \
    content. For example: \
    [
        {"example.com":
            {"type": "A", "name": "host1", "content": "192.0.2.1"}
        },
        {"1.2.0.192.in-addr.arpa":
            {"type": "PTR", "name": "1", "content": "name1.example.com"}
        },
    ]
    """
    hostname = kwargs["hostname"]
    if not hostname:
        raise AttributeError("A hostname is required")
    domain_attr = {}
    hosts = hostname.split(".")
    domains = hosts[-2:]
    host = hosts[0:-2:]
    domain_attr["fqdn"] = hostname
    domain_attr["domain"] = f"{domains[0]}.{domains[1]}"
    domain_attr["host"] = ".".join(host)
    records_list = []
    if kwargs["ipv4"]:
        try:
            ipv4 = ipaddress.ip_address(kwargs["ipv4"])
            z_reverse4_full = (
                ipaddress.ip_network(ipv4)
                .supernet(new_prefix=24)
                .network_address.reverse_pointer
            )
            z_reverse4 = ".".join(z_reverse4_full.split(".")[1:])
            #
            forward_4 = {
                domain_attr["domain"]: {
                    "type": "A",
                    "name": domain_attr["fqdn"],
                    "content": str(ipv4),
                }
            }
            records_list.append(forward_4)
            reverse_4 = {
                z_reverse4: {
                    "type": "PTR",
                    "name": str(ipv4).split(".")[3],
                    "content": hostname,
                }
            }
            records_list.append(reverse_4)
        except ValueError:
            raise AttributeError(f"{ipv4} is an invalid IPv4 Address")
    if kwargs["ipv6"]:
        try:
            ipv6 = ipaddress.ip_address(kwargs["ipv6"])
            z_reverse_list = str(ipv6.reverse_pointer).split(".")
            z_reverse6 = ".".join(z_reverse_list[-10:])
            z_reverse6_host = ".".join(z_reverse_list[0:-10:])
            #
            forward_6 = {
                domain_attr["domain"]: {
                    "type": "AAAA",
                    "name": domain_attr["fqdn"],
                    "content": str(ipv6),
                }
            }
            records_list.append(forward_6)
            #
            reverse_6 = {
                z_reverse6: {
                    "type": "PTR",
                    "name": z_reverse6_host,
                    "content": hostname,
                }
            }
            records_list.append(reverse_6)
        except ValueError:
            raise AttributeError(f"{ipv6} is an invalid IPv6 Address")
    return records_list
