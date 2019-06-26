# Deenis
*Named in honor of those who simply must make all acronyms pronouncable.*

Deenis is a **work in progress** tool used to consolidate and automate boring DNS tasks. Current list of available functions:

| Name   | Purpose                                                                                                                                                           |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `host` | For a single host, such as `name.example.com`, with corresponding IPv4 and IPv6 addresses, constructs A, AAAA, and PTR records and adds them via Public DNS APIs. |

## Important Exceptions

### Supported Providers
Currently, only [Cloudflare DNS](https://www.cloudflare.com/dns/) is supported, however Deenis is built to work with multiple configurable providers.

### Assumptions
Currently, it is assumed that the same provider is used for all record types. I.e., if adding the following record set:

| Record Type | Name                                                                       | Target             |
| ----------- | -------------------------------------------------------------------------- | ------------------ |
|    **A**    | `name.example.com`                                                         | `192.0.2.1`        |
|   **AAAA**  | `name.example.com`                                                         | `2001:db8::1`      |
|   **PTR**   | `1.2.0.192.in-addr.arpa`                                                   | `name.example.com` |
|   **PTR**   | `1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa` | `name.example.com` |

It is assumed that the selected DNS provider is authoritative for **all** of the `example.com`, `2.0.192.in-addr.arpa` `0.8.b.d.0.1.0.0.2.ip6.arpa` zones. This is *probably* not the case for most people, but is the case for the original purpose for throwing Deenis together. This is not permanent, there is already *some* logic in place to undo this later.

## Installation

### Clone the Repository

```console
$ git clone https://github.com/checktheroads/deenis.git
$ pip3 install -r requirements.txt
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

```python
import deenis

records = deenis.host("192.0.2.1", "2001:db8::1", "name.example.com")

for record in records:
    print(record)
# {'success': True, 'message': 'Added A Record for name.example.com, pointing to 192.0.2.1'}
# {'success': True, 'message': 'Added PTR Record for 250.95.34.199.in-addr.arpa, pointing to name.example.com'}
# {'success': True, 'message': 'Added AAAA Record for name.example.com, pointing to 2001.db8::1'}
# {'success': True, 'message': 'Added PTR Record for 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa, pointing to name.example.com'}
```

### As a CLI Tool

#### Shell Script

A *very* simple shell script is included to essentially alias the execution of `cli.py`. If you want `deenis.sh` to be somewhere in your `$PATH`, set the `DEENIS_PATH` variable:

```console
$ nano deenis/deenis.sh
DEENIS_PATH="/home/you/deenis/deenis"
```
And copy away: `cp deenis/deenis.sh /usr/local/bin/deenis`

```console
# deenis --help
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  Deenis can be used to group and automate boring DNS tasks. For example,
  `host` can take a hostname, IPv4 Address, and IPv6 Address, and create
  forward A & AAAA, and reverse PTR records (4 actions) with a single
  command.

Options:
  --help  Show this message and exit.

Commands:
  host  Add a Host Record
```

#### Python Script

Depending on your use case, you can also bypass the whole shell script thing by just executing `cli.py` directly:

```console
$ cd deenis/deenis
$ python3 cli.py host --help
Usage: cli.py host [OPTIONS]

  Add a Host Record

Options:
  -4, --ipv4 TEXT  IPv4 Address
  -6, --ipv6 TEXT  IPv6 Address
  -f, --fqdn TEXT  FQDN  [required]
  --help           Show this message and exit.
```

# License
<a href="http://www.wtfpl.net/"><img src="http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png" width="80" height="15" alt="WTFPL" /></a>
