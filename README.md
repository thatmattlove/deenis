# Deenis

_Named in honor of those who simply must make all acronyms pronouncable._

Deenis is a **work in progress** tool used to consolidate and automate boring DNS tasks. Current list of available functions:

| Name     | Purpose                                                                                                                                                                                                                          |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `host`   | For a single host, such as `name.example.com`, with corresponding IPv4 and IPv6 addresses, constructs A, AAAA, and PTR records and adds them via Public DNS APIs.                                                                |
| `tenant` | For a customer/tenant identifier, such as `12345`, with corresponding IPv4 and IPv6 prefixes, PTR records for every IP in the IPv4 assignment, and a wildcard record for the IPv6 assignment, and adds them via Public DNS APIs. |

## Important Exceptions

### Supported Providers

Currently, only [Cloudflare DNS](https://www.cloudflare.com/dns/) is supported, however Deenis is built to work with multiple configurable providers.

## Installation

```console
$ pip3 install git+https://github.com/checktheroads/deenis.git
```

## Usage

### As a Python Module

Deenis needs to be initialized with a configuration. This can be a dictionary or otherwise imported configuration from your main project, or the aboslute path to a YAML configuration file can be used. Pythonically cheeky example provided below:

```python
import deenis

deenis_config = None

if your_preference is "dict":
    deenis_config = {
      'debug': False,
      'provider': {
          'cloudflare': {
              'api': {
                  'baseurl':
                      'https://api.cloudflare.com/client/v4/',
                      'email': 'name@example.com',
                      'key': '1234'
              }
            },
      },
      'zone': {
          '0.8.b.d.0.1.0.0.2.ip6.arpa': {
              'direction': 'reverse',
              'providers': ['cloudflare']
          },
          '2.0.192.in-addr.arpa': {
              'direction': 'reverse',
              'providers': ['cloudflare']
          },
          'example.com': {
              'direction': 'forward',
              'providers': ['cloudflare']
          },
      }
    }
elif your_preference is "file":
    from pathlib import Path
    deenis_config = Path().resolve().joinpath("deenis.yaml")

# Initialize the module with a configuration
dns = deenis.Deenis(deenis_config)

# Parameters for the host function
host_to_add = {
  "hostname": "name.example.com",
  "ipv4": "192.0.2.1",
  "ipv6": "2001:db8::1",
}
results = dns.AddHost(host_to_add)

for result in results:
    print(result)
('Success', 'PTR', '254', '12345.test011.example.com', [])

# ('Success', 'A', name, '192.0.2.1', [])
# ('Success', 'PTR', 250, 'name.example.com', [])
# ('Success', 'AAAA', name, '2001.db8::1', [])
# ('Success', 'PTR', 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0, 'name.example.com', [])

# Paramters for the target function
new_customer_info = {
    "crm_id": 12345,
    "host4": "ip4.example.com",
    "host6": "ip6.example.com",
    "prefix4": "192.0.2.0/28",
    "prefix6": "2001:db8::/48"
}

results = dns.TenantReverse(new_customer_info)

for result in results:
    print(result)
# ('Success', 'PTR', '0', '12345.ip4.example.com', [])
# ('Success', 'PTR', '1', '12345.ip4.example.com', [])
# ('Success', 'PTR', '2', '12345.ip4.example.com', [])
# ('Success', 'PTR', '3', '12345.ip4.example.com', [])
# ('Success', 'PTR', '4', '12345.ip4.example.com', [])
# ('Success', 'PTR', '5', '12345.ip4.example.com', [])
# ('Success', 'PTR', '6', '12345.ip4.example.com', [])
# ('Success', 'PTR', '7', '12345.ip4.example.com', [])
# ('Success', 'PTR', '8', '12345.ip4.example.com', [])
# ('Success', 'PTR', '9', '12345.ip4.example.com', [])
# ('Success', 'PTR', '10', '12345.ip4.example.com', [])
# ('Success', 'PTR', '11', '12345.ip4.example.com', [])
# ('Success', 'PTR', '12', '12345.ip4.example.com', [])
# ('Success', 'PTR', '13', '12345.ip4.example.com', [])
# ('Success', 'PTR', '14', '12345.ip4.example.com', [])
# ('Success', 'PTR', '15', '12345.ip4.example.com', [])
# ('Success', 'PTR', '*.f.e.f.e', '12345.ip6.example.com', [])
```
### As a CLI Tool

When running as a CLI tool, a config file must be provided. An example has been provided in `examples/deenis.yaml`. A path can be provided, or if `deenis.yaml` is in the current directory (and a path is not specified) it will be used.

#### Host

```console
$ deenis host --help
Usage: deenis host [OPTIONS]

  Add a Host Record

Options:
  -c, --config-file TEXT   Path to TOML Config File  [required]
  -4, --ipv4-address TEXT  IPv4 Address
  -6, --ipv6-address TEXT  IPv6 Address
  -f, --fqdn TEXT          FQDN  [required]
  --help                   Show this message and exit.
```

#### Tenant

```console
$ deenis tenant --help
Usage: cli.py tenant [OPTIONS]

  Bulk Add PTR Records for a Tenant/Customer

Options:
  -c, --config-file TEXT  Path to YAML Config File
  -i, --crm-id TEXT       Unique Tenant Indentifier
  -4, --ipv4-prefix TEXT  IPv4 Prefix Assignment
  -6, --ipv6-prefix TEXT  IPv6 Prefix Assignment
  -f4, --ipv4-fqdn TEXT   FQDN for IPv4 PTR Target
  -f6, --ipv6-fqdn TEXT   FQDN for IPv6 PTR Target
  --help                  Show this message and exit.
```

# License

<a href="http://www.wtfpl.net/"><img src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png" width="80" height="15" alt="WTFPL" /></a>
