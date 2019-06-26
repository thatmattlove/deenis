"""
Imports and Exports Config File Variables
"""
# Standard Imports
import os

# Module Imports
import toml

# Config File Definitions
project_root = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(project_root, "config.toml")
conf = toml.load(config_file)

msg_keyerror = "{key} is not defined in {file}"


def debug_state():
    """Returns boolean for logzero log level"""
    state = conf.get("debug", False)
    return state


def zone(z_name):
    """Returns zone configuration parameters for input zone name"""
    try:
        z_conf = conf["zone"].get(z_name, None)
        return z_conf
    except KeyError as missing_key:
        raise RuntimeError(msg_keyerror.format(key=missing_key, file=config_file))


def api(prov):
    """Returns API configuration parameters for input provider name"""
    try:
        api_dict = {}
        api_dict["baseurl"] = conf["provider"][prov]["api"].get("baseurl", None)
        api_dict["email"] = conf["provider"][prov]["api"].get("email", None)
        api_dict["key"] = conf["provider"][prov]["api"].get("key", None)
        return api_dict
    except KeyError as missing_key:
        raise RuntimeError(msg_keyerror.format(key=missing_key, file=config_file))


def providers():
    """Returns list of all configured providers"""
    try:
        prov_list = []
        for prov in conf["provider"]:
            prov_list.append(prov)
        return prov_list
    except KeyError as missing_key:
        raise RuntimeError(msg_keyerror.format(key=missing_key, file=config_file))
