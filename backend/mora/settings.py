# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""
    settings.py
    ~~~~~~~~~~~

    This module contains all global ``os2mo`` settings.

    The variables available and their defaults are defined in
    ``default-settings.toml``. Furthermore, $OS2MO_SYSTEM_CONFIG_PATH and
    $OS2MO_USER_CONFIG_PATH are environment variables, that can be used
    to point at other config files.

    The config file precedens is:
        default-settings.toml
        < $OS2MO_SYSTEM_CONFIG_PATH
        < $OS2MO_USER_CONFIG_PATH

    default-settings.toml: reference file and default values.
    $OS2MO_SYSTEM_CONFIG_PATH: config for system environment e.g. docker.
    $OS2MO_USER_CONFIG_PATH: this is where you write your configuration.
"""

import copy
import json

import logging
import pprint
import os
import sys

import toml

logger = logging.getLogger(__name__)

DEPRECATED_SETTINGS = {
    'log': {
        'activity_log_path': "",
        'trace_log_path': ""
    }
}


def read_config(config_path):
    try:
        with open(config_path) as f:
            content = f.read()
    except FileNotFoundError as err:
        logger.critical("%s: %r", err.strerror, err.filename)
        sys.exit(5)
    try:
        return toml.loads(content)
    except toml.TomlDecodeError:
        logger.critical("Failed to parse TOML")
        sys.exit(4)


def update_dict(base_dict: dict, new_dict: dict):
    """
    Update base_dict with values found in new_dict recursively
    """
    for key in new_dict:
        if key in base_dict.keys():
            if isinstance(base_dict.get(key), dict):
                update_dict(base_dict[key], new_dict[key])
            else:
                base_dict[key] = new_dict[key]
        else:
            base_dict[key] = new_dict[key]


def dict_key_intersection(d1: dict, d2: dict) -> dict:
    """
    Return intersection of the keys of two nested dicts d1 and d2.
    """
    if not d1 or not d2:
        return {}

    intersection = {}
    for key in d1.keys():
        if key in d2.keys():
            if isinstance(d1[key], dict):
                result = dict_key_intersection(d1[key], d2[key])
                if result:
                    intersection[key] = result
            else:
                intersection[key] = d2[key]
    return intersection


def dict_key_difference(d1: dict, d2: dict) -> dict:
    """
    Return the nested structure of keys that are in d2 but not in d1
    """
    if not d1:
        return d2
    if not d2:
        return d1

    difference = {}
    for key in d2.keys():
        if key in d1.keys():
            if isinstance(d1[key], dict):
                result = dict_key_difference(d1[key], d2[key])
                if result:
                    difference[key] = result
        else:
            difference[key] = d2[key]
    return difference


def check_and_update_config(configuration, new_config):
    """
    Check if given configuration object contains any invalid or deprecated keys,
    and merge into existing config
    """
    check_deprecated_settings(new_config)
    check_invalid_settings(new_config)
    update_dict(configuration, new_config)


def check_deprecated_settings(configuration: dict):
    """Check if given configuration contains deprecated config entries"""
    intersection = dict_key_intersection(DEPRECATED_SETTINGS, configuration)
    if intersection:
        logger.warning(
            "Deprecated key(s) in config: {}".format(json.dumps(intersection)))


def check_invalid_settings(configuration: dict):
    """Check if given configuration contains invalid config entries"""
    # We merge our default settings with the deprecated settings to get all valid keys
    combined_settings = copy.deepcopy(config)
    update_dict(combined_settings, DEPRECATED_SETTINGS)
    difference = dict_key_difference(combined_settings, configuration)
    if difference:
        logger.warning("Invalid key(s) in config: {}".format(json.dumps(difference)))


def log_config(configuration):
    """
    Log a config object, hiding all passwords
    :param configuration: A config object to be logged
    """
    safe_config = copy.deepcopy(configuration)
    safe_config["configuration"]["database"]["password"] = "********"
    logger.debug("Config:\n%s.", pprint.pformat(safe_config))
    logger.info("Config: %s.", safe_config)


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_settings_path = os.path.join(base_dir, "mora", "default-settings.toml")
with open(default_settings_path, "r") as f:
    # DO NOT print or log ``config`` as it will EXPOSE the PASSWORD
    config = toml.load(f)

system_config_path = os.getenv("OS2MO_SYSTEM_CONFIG_PATH", False)
user_config_path = os.getenv("OS2MO_USER_CONFIG_PATH", False)
if system_config_path:
    logger.info("Reading system config from %s", system_config_path)
    check_and_update_config(config, read_config(system_config_path))
if user_config_path:
    logger.info("Reading user config from %s", user_config_path)
    check_and_update_config(config, read_config(user_config_path))

log_config(config)

# This object is used with ``app.config.update`` in app.py.
app_config = {
    "QUERY_EXPORT_DIR": config["query_export"]["directory"],
    "TRIGGER_MODULES": config["triggers"]["modules"],

    # Set to 'None' specifically if unset to retain default behavior in flask
    "SERVER_NAME": config["server_name"] or None,
    "ENABLE_CORS": config["enable_cors"] or False,

    # serviceplatformen
    "DUMMY_MODE": config["dummy_mode"],
    "SP_SERVICE_UUID": config['service_platformen']['uuid'],
    "SP_SERVICE_AGREEMENT_UUID":
        config['service_platformen']['agreement_uuid'],
    "SP_MUNICIPALITY_UUID": config['service_platformen']['municipality_uuid'],
    "SP_SYSTEM_UUID": config['service_platformen']['system_uuid'],
    "SP_CERTIFICATE_PATH": config['service_platformen']['certificate_path'],

    # amqp
    "ENABLE_AMQP": config["amqp"]["enable"],
    "AMQP_OS2MO_EXCHANGE": config["amqp"]["os2mo_exchange"],
    "AMQP_HOST": config["amqp"]["host"],
    "AMQP_PORT": config["amqp"]["port"],
}

# All these variables are kept for backward compatibility / to change the least
# code. From now on, use the ``config`` object in this module. At this point,
# it would be fine to go through the code and get rid of the old variables,
# although it might be non-trivial, especially for the test suite.


LORA_URL = config['lora']['url']
# CA_BUNDLE = config['ca_bundle']  DEPRECATED
AUTOCOMPLETE_ACCESS_ADDRESS_COUNT = (
    config['autocomplete']['access_address_count'])
AUTOCOMPLETE_ADDRESS_COUNT = config['autocomplete']['address_count']
ORGANISATION_NAME = config['organisation']['name']
ORGANISATION_USER_KEY = config['organisation']['user_key']
ORGANISATION_UUID = config['organisation']['uuid']
SP_SERVICE_UUID = config['service_platformen']['uuid']
SP_SERVICE_AGREEMENT_UUID = config['service_platformen']['agreement_uuid']
SP_MUNICIPALITY_UUID = config['service_platformen']['municipality_uuid']
SP_SYSTEM_UUID = config['service_platformen']['system_uuid']
SP_CERTIFICATE_PATH = config['service_platformen']['certificate_path']
DUMMY_MODE = config['dummy_mode']
HIDE_CPR_NUMBERS = config['hide_cpr_numbers']
QUERY_EXPORT_DIR = config['query_export']['directory']
ENABLE_AMQP = config['amqp']['enable']
AMQP_OS2MO_EXCHANGE = config['amqp']['os2mo_exchange']
AMQP_HOST = config['amqp']['host']
AMQP_PORT = config['amqp']['port']
TRIGGER_MODULES = config['triggers']['modules']
