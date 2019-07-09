"""
Constructs Usable Data Structures for use by APIs
"""
# Standard Library Imports
import ipaddress


def record_a(zone_in, host_in, ip_in):
    """Validates and constructs A record parameters."""
    try:
        ip_out = ipaddress.ip_address(ip_in)
        record = {zone_in: {"type": "A", "name": host_in, "content": str(ip_out)}}
    except ValueError:
        raise AttributeError(f"{ip_in} is an invalid IPv4 Address")
    return record


def record_aaaa(zone_in, host_in, ip_in):
    """Validates and constructs AAAA record parameters."""
    try:
        ip_out = ipaddress.ip_address(ip_in)
        record = {zone_in: {"type": "AAAA", "name": host_in, "content": str(ip_out)}}
    except ValueError:
        raise AttributeError(f"{ip_in} is an invalid IPv6 Address")
    return record


def record_ptr4(host_in, ip_in):
    """Validates and constructs PTR record parameters for IPv4."""
    try:
        prefix_len = ipaddress.ip_network(ip_in).prefixlen
        if prefix_len == 32:
            ip_out = ipaddress.ip_address(ip_in)
        elif prefix_len < 32:
            ip_out = ipaddress.ip_network(ip_in)
        z_reverse_full = (
            ipaddress.ip_network(ip_out)
            .supernet(new_prefix=24)
            .network_address.reverse_pointer
        )
        z_reverse = ".".join(z_reverse_full.split(".")[1:])
        record = {
            z_reverse: {
                "type": "PTR",
                "name": str(ip_out).split(".")[3],
                "content": host_in,
            }
        }
    except ValueError:
        raise AttributeError(f"{ip_in} is an invalid IPv4 Address")
    return record


def record_ptr6(host_in, ip_in):
    """Validates and constructs PTR record parameters for IPv6."""
    nibs = {32: -10, 36: -11, 40: -12, 44: -13, 48: -14, 52: -15, 56: -16}
    try:
        prefix_len = ipaddress.ip_network(ip_in).prefixlen
        if prefix_len not in nibs.keys():
            nib_list = list(nibs.keys())
            raise AttributeError(
                (
                    f"IPv6 subnet must be on a nibble boundary between {nib_list[0]} "
                    f"and {nib_list[-1]}"
                )
            )
        if prefix_len == 128:
            ip_out = ipaddress.ip_address(ip_in)
            z_reverse_list = str(ip_out.reverse_pointer).split(".")
            z_reverse = ".".join(z_reverse_list[-10:])
            z_reverse_host = ".".join(z_reverse_list[0 : nibs.get(32) :])
        elif prefix_len < 128:
            ip_out = ipaddress.ip_network(ip_in).network_address
            z_reverse_list = str(ip_out.reverse_pointer).split(".")
            z_reverse = ".".join(z_reverse_list[-10:])
            z_reverse_host_list = z_reverse_list[nibs.get(prefix_len) : nibs.get(32) :]
            z_reverse_host_list.insert(0, "*")
            z_reverse_host = ".".join(z_reverse_host_list)
        record = {
            z_reverse: {"type": "PTR", "name": z_reverse_host, "content": host_in}
        }
    except ValueError:
        raise AttributeError(f"{ip_in} is an invalid IPv6 Address")
    return record


def host_data(fqdn):
    """
    Splits input FQDN to usable elements:

    domain_attr = {
        "fqdn": "name.example.com",
        "domain": "example.com",
        "host": "name",
    }
    Takes into account multiple subdomains
    (i.e., name1.name2.example.com).
    """
    hosts = fqdn.split(".")
    domain_attr = {
        "fqdn": fqdn,
        "domain": hosts[-2:][0] + "." + hosts[-2:][1],
        "host": ".".join(hosts[0:-2:]),
    }
    return domain_attr


def host_records(**kwargs):
    """
    Builds list of nested dicts where each parent key is the zone, and
    each zone's child dict contains a k/v of DNS record type (A, AAAA,
    PTR, etc.), DNS record name, and DNS record content. For example:
    [
        {"example.com":
            {"type": "A", "name": "host1", "content": "192.0.2.1"}
        },
        {"1.2.0.192.in-addr.arpa":
            {"type": "PTR", "name": "1", "content": "name1.example.com"}
        },
    ]
    """
    if not kwargs["hostname"]:
        raise AttributeError("A hostname is required")
    domain_attr = host_data(kwargs["hostname"])
    records_list = []
    if kwargs["ipv4"]:
        records_list.append(
            record_a(domain_attr["domain"], kwargs["hostname"], kwargs["ipv4"])
        )
        records_list.append(record_ptr4(domain_attr["fqdn"], kwargs["ipv4"]))
    if kwargs["ipv6"]:
        records_list.append(
            record_aaaa(domain_attr["domain"], kwargs["hostname"], kwargs["ipv6"])
        )
        records_list.append(record_ptr6(domain_attr["fqdn"], kwargs["ipv6"]))
    return records_list


def tenant_records(crm_id=None, host4=None, host6=None, prefix4=None, prefix6=None):
    """
    Constructs list of reverse DNS records based on input values.
    Intended to solve the problem of reverse DNS for customer IP
    subassignments smaller than /24.

    Example: for 192.0.2.0/28, builds and adds all 16 individual PTR
    records based on a customer ID or other identifier.

    For IPv6, a wildcard record is created for the entire customer
    subassignment.

    Input Format:
    {
        "crm_id": 12345,
        "host4": "ip4.example.com",
        "host6": "ip6.example.com",
        "prefix4": "192.0.2.0/28",
        "prefix6": "2001:db8::/48"
    }
    """
    # pylint: disable=too-many-branches
    if prefix4:
        try:
            addrlist4 = [ip for ip in ipaddress.ip_network(prefix4)]
        except ValueError:
            raise AttributeError(f"{prefix4} is not a valid IPv4 Address.")
    if prefix6:
        try:
            addrlist6 = ipaddress.ip_network(prefix6)
        except ValueError:
            raise AttributeError(f"{prefix6} is not a valid IPv4 Address.")

    if prefix4 and host4:
        target4 = host4
    elif prefix4 and host6 and not host4:
        target4 = host6
    elif prefix4 and not host4 and not host6:
        raise AttributeError("No hostname was provided as a PTR target")
    if prefix6 and host6:
        target6 = host6
    elif prefix6 and host4 and not host6:
        target6 = host4
    elif prefix6 and not host4 and not host6:
        raise AttributeError("No hostname was provided as a PTR target")
    if crm_id:
        target4 = ".".join([crm_id, target4])
        target6 = ".".join([crm_id, target6])
    records_list = []
    if prefix4:
        for addr in addrlist4:
            records_list.append(record_ptr4(target4, str(addr)))
    if prefix6:
        records_list.append(record_ptr6(target6, str(addrlist6)))
    elif prefix6 and host4 and not host6:
        records_list.append(record_ptr6(host4, str(addrlist6)))
    if not records_list:
        raise RuntimeError("No records were created.")
    return records_list
