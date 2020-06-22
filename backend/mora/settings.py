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
    safe_config["session"]["database"]["password"] = "********"
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

    # These two are *not* used by flask_saml_sso:
    "SAML_USERNAME_FROM_NAMEID": config["saml_sso"]["username_from_nameid"],
    "SAML_USERNAME_ATTR": config["saml_sso"]["username_attr"],

    # The remaining key/value pairs are for flask_saml_sso. flask_saml_sso has
    # many configuration parameters. The module reads its' configuration from
    # keys on the app.config object. Here is the mapping between the module's
    # settings and their names in the os2mo configuration. You can read what
    # all the options do in the official documentation:
    # https://flask-saml-sso.readthedocs.io/en/latest/README.html#configuration
    "SAML_AUTH_ENABLE": config["saml_sso"]["enable"],
    "SAML_IDP_INSECURE": config["saml_sso"]["idp_insecure"],
    "SAML_FORCE_HTTPS": config["saml_sso"]["force_https"],
    "SAML_SP_DOMAIN": config["saml_sso"]["sp_domain"],
    "SAML_NAME_ID_FORMAT": config["saml_sso"]["name_id_format"],
    "SAML_WANT_NAME_ID": config["saml_sso"]["want_name_id"],
    "SAML_WANT_ATTRIBUTE_STATEMENT":
        config["saml_sso"]["want_attribute_statement"],
    "SAML_REQUESTED_AUTHN_CONTEXT":
        config["saml_sso"]["requested_authn_context"],
    "SAML_REQUESTED_AUTHN_CONTEXT_COMPARISON":
        config["saml_sso"]["requested_authn_context_comparison"],
    "SAML_LOWERCASE_URLENCODING": config["saml_sso"]["lowercase_urlencoding"],
    "SAML_REQUESTS_SIGNED": config["saml_sso"]["requests_signed"],
    "SAML_CERT_FILE": config["saml_sso"]["cert_file"],
    "SAML_KEY_FILE": config["saml_sso"]["key_file"],
    "SAML_SIGNATURE_ALGORITHM": config["saml_sso"]["signature_algorithm"],
    "SAML_DIGEST_ALGORITHM": config["saml_sso"]["digest_algorithm"],
    "SAML_IDP_METADATA_URL": config["saml_sso"]["idp_metadata_url"],
    "SAML_IDP_METADATA_FILE": config["saml_sso"]["idp_metadata_file"],
    "SAML_DUPLICATE_ATTRIBUTES": config["saml_sso"]["duplicate_attributes"],
    "SQLALCHEMY_DATABASE_URI": config["session"]["database"]["sqlalchemy_uri"],
    "SESSION_SQLALCHEMY_TABLE":
        config["session"]["database"]["sqlalchemy_table"],
    "SESSIONS_DB_USER": config["session"]["database"]["user"],
    "SESSIONS_DB_PASSWORD": config["session"]["database"]["password"],
    "SESSIONS_DB_HOST": config["session"]["database"]["host"],
    "SESSIONS_DB_PORT": config["session"]["database"]["port"],
    "SESSIONS_DB_NAME": config["session"]["database"]["name"],
    "SESSION_PERMANENT": config["session"]["permanent"],
    "PERMANENT_SESSION_LIFETIME": config["session"]["permanent_lifetime"],
    "SAML_SERVICE_SESSION_LIFETIME":
        config["session"]["service_session_lifetime"],
    "SESSION_COOKIE_NAME": config["session"]["cookie_name"],
    "SAML_API_TOKEN_RESTRICT": config["saml_sso"]["api_token_restrict"],
    "SAML_API_TOKEN_RESTRICT_ATTR":
        config["saml_sso"]["api_token_restrict_attr"],
    "SAML_API_TOKEN_RESTRICT_VALUE":
        config["saml_sso"]["api_token_restrict_value"],
}


# All these variables are kept for backward compatibility / to change the least
# code. From now on, use the ``config`` object in this module. At this point,
# it would be fine to go through the code and get rid of the old variables,
# although it might be non-trivial, especially for the test suite.


MAX_REQUEST_LENGTH = config['lora']['max_request_length']
DEFAULT_PAGE_SIZE = config['lora']['default_page_size']
TREE_SEARCH_LIMIT = config['lora']['tree_search_limit']
LORA_URL = config['lora']['url']
CA_BUNDLE = config['ca_bundle']
AUTOCOMPLETE_ACCESS_ADDRESS_COUNT = (
    config['autocomplete']['access_address_count'])
AUTOCOMPLETE_ADDRESS_COUNT = config['autocomplete']['address_count']
ORGANISATION_NAME = config['organisation']['name']
ORGANISATION_USER_KEY = config['organisation']['user_key']
ORGANISATION_UUID = config['organisation']['uuid']
SQLALCHEMY_DATABASE_URI = config['session']['database']['sqlalchemy_uri']
SESSION_SQLALCHEMY_TABLE = config['session']['database']['sqlalchemy_table']
SESSION_PERMANENT = config['session']['permanent']
PERMANENT_SESSION_LIFETIME = config['session']['permanent_lifetime']
SESSIONS_DB_NAME = config['session']['database']['name']
SESSIONS_DB_USER = config['session']['database']['user']
SESSIONS_DB_PASSWORD = config['session']['database']['password']
SESSIONS_DB_HOST = config['session']['database']['host']
SESSIONS_DB_PORT = config['session']['database']['port']
SAML_AUTH_ENABLE = config['saml_sso']['enable']
SAML_IDP_METADATA_URL = config['saml_sso']['idp_metadata_url']
SAML_IDP_METADATA_FILE = config['saml_sso']['idp_metadata_file']
SAML_IDP_INSECURE = config['saml_sso']['idp_insecure']
SAML_USERNAME_FROM_NAMEID = config['saml_sso']['username_from_nameid']
SAML_USERNAME_ATTR = config['saml_sso']['username_attr']
SAML_KEY_FILE = config['saml_sso']['key_file']
SAML_CERT_FILE = config['saml_sso']['cert_file']
SAML_REQUESTS_SIGNED = config['saml_sso']['requests_signed']
SAML_DUPLICATE_ATTRIBUTES = config['saml_sso']['duplicate_attributes']
SAML_API_TOKEN_RESTRICT = config['saml_sso']['api_token_restrict']
SAML_API_TOKEN_RESTRICT_ATTR = config['saml_sso']['api_token_restrict_attr']
SAML_API_TOKEN_RESTRICT_VALUE = config['saml_sso']['api_token_restrict_value']
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
