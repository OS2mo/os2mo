#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

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
import logging
import pprint
import os
import sys

import toml


logger = logging.getLogger(__name__)


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


def update_config(configuration, new_settings):
    # we cannot just do dict.update, because we do not want to "polute" the
    # namespace with anything in *new_settings*, just the variables defined in
    # **configuration**.
    for key in new_settings:
        if key in configuration:
            if isinstance(configuration[key], dict):
                update_config(configuration[key], new_settings[key])
            else:
                configuration[key] = new_settings[key]
        else:
            logger.warning("Invalid key in config: %s", key)


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_settings_path = os.path.join(base_dir, "mora", "default-settings.toml")
with open(default_settings_path, "r") as f:
    # DO NOT print or log ``config`` as it will EXPOSE the PASSWORD
    config = toml.load(f)

system_config_path = os.getenv("OS2MO_SYSTEM_CONFIG_PATH", False)
user_config_path = os.getenv("OS2MO_USER_CONFIG_PATH", False)
if system_config_path:
    logger.info("Reading system config from %s", system_config_path)
    update_config(config, read_config(system_config_path))
if user_config_path:
    logger.info("Reading user config from %s", user_config_path)
    update_config(config, read_config(user_config_path))


safe_config = copy.deepcopy(config)
safe_config["session"]["database"]["password"] = "********"
safe_config["configuration"]["database"]["password"] = "********"
logger.debug("Config:\n%s.", pprint.pformat(safe_config))
logger.info("Config: %s.", safe_config)
del safe_config  # could get out of sync


# This object is used with ``app.config.update`` in app.py.
app_config = {
    "QUERY_EXPORT_DIR": config["query_export"]["directory"],
    "TRIGGER_MODULES": config["triggers"]["modules"],

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
CONF_DB_NAME = config['configuration']['database']['name']
CONF_DB_USER = config['configuration']['database']['user']
CONF_DB_PASSWORD = config['configuration']['database']['password']
CONF_DB_HOST = config['configuration']['database']['host']
CONF_DB_PORT = config['configuration']['database']['port']
QUERY_EXPORT_DIR = config['query_export']['directory']
ENABLE_AMQP = config['amqp']['enable']
AMQP_OS2MO_EXCHANGE = config['amqp']['os2mo_exchange']
AMQP_HOST = config['amqp']['host']
AMQP_PORT = config['amqp']['port']
TRIGGER_MODULES = config['triggers']['modules']
