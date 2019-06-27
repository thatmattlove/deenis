# Deenis
*Named in honor of those who simply must make all acronyms pronouncable.*

Deenis is a **work in progress** tool used to consolidate and automate boring DNS tasks. Current list of available functions:

| Name   | Purpose                                                                                                                                                           |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `host` | For a single host, such as `name.example.com`, with corresponding IPv4 and IPv6 addresses, constructs A, AAAA, and PTR records and adds them via Public DNS APIs. |

## Important Exceptions

### Supported Providers
Currently, only [Cloudflare DNS](https://www.cloudflare.com/dns/) is supported, however Deenis is built to work with multiple configurable providers.

## Installation

```console
$ pip3 install git+https://github.com/checktheroads/deenis.git
```

## Configuration

### Copy Example TOML Config File

```console
$ cp deenis/config.toml.example deenis/config.toml
$ nano deenis/config.toml
```

### Modify Config Variables

```toml
debug = false

[provider.cloudflare.api]
baseurl = "https://api.cloudflare.com/client/v4/"
email = "name@example.com"
key = "1234"

[zone.'example.com']
providers = ["cloudflare"]
direction = "forward"
```

*Note: the* `[zone]` *table is not used for anything yet.*

## Usage

### As a Python Module

Deenis needs to be initialized with a configuration. This can be a dictionary or otherwise imported configuration from your main project, or the aboslute path to a TOML configuration file can be used. Pythonically cheeky example provided below:

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
  deenis_config = os.path.join(os.path.abspath("."), "config.toml")

# Initialize the module with a configuration
dns = deenis.Deenis(deenis_config)

# Parameters for the host function
host_to_add = {
  "hostname": "name.example.com",
  "ipv4": "192.0.2.1",
  "ipv6": "2001:db8::1",
}
records = dns.AddHost(host_to_add)

for record in records:
    print(record)
# {'success': True, 'message': 'Added A Record for name.example.com, pointing to 192.0.2.1'}
# {'success': True, 'message': 'Added PTR Record for 250.95.34.199.in-addr.arpa, pointing to name.example.com'}
# {'success': True, 'message': 'Added AAAA Record for name.example.com, pointing to 2001.db8::1'}
# {'success': True, 'message': 'Added PTR Record for 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa, pointing to name.example.com'}
```

### As a CLI Tool

When running as a CLI tool, a config file must be provided. An example has been provided in `deenis/config.toml.example`

```console
$ deenis --help
Usage: deenis host [OPTIONS]

  Add a Host Record

Options:
  -c, --config-file TEXT   Path to TOML Config File  [required]
  -4, --ipv4-address TEXT  IPv4 Address
  -6, --ipv6-address TEXT  IPv6 Address
  -f, --fqdn TEXT          FQDN  [required]
  --help                   Show this message and exit.
```

# License
<a href="http://www.wtfpl.net/"><img src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png" width="80" height="15" alt="WTFPL" /></a>
