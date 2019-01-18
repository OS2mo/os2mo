#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from os import path as _path, getenv

from . import util as _util

BASE_DIR = _path.dirname(_path.dirname(_path.abspath(__file__)))
CONFIG_FILE = getenv('OS2MO_CONFIG_FILE',
                     _path.join(BASE_DIR, '..', 'setup', 'mora.json'))

MAX_REQUEST_LENGTH = 4096
DEFAULT_PAGE_SIZE = 2000
TREE_SEARCH_LIMIT = 100

LORA_URL = 'http://localhost:8080/'
CA_BUNDLE = None

# for our autocomplete support
AUTOCOMPLETE_ACCESS_ADDRESS_COUNT = 5
AUTOCOMPLETE_ADDRESS_COUNT = 10

# Session config
SQLALCHEMY_DATABASE_URI = ""
SESSION_SQLALCHEMY_TABLE = 'sessions'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = 3600

# SSO config
SAML_AUTH_ENABLE = False
SAML_IDP_METADATA_URL = '/url/to/sso/metadata'
SAML_IDP_METADATA_FILE = None
SAML_IDP_INSECURE = False
SAML_USERNAME_ATTR = ''
SAML_KEY_FILE = None
SAML_CERT_FILE = None
SAML_REQUESTS_SIGNED = False
SAML_DUPLICATE_ATTRIBUTES = True
SAML_API_TOKEN_RESTRICT = False
SAML_API_TOKEN_RESTRICT_ATTR = ""
SAML_API_TOKEN_RESTRICT_VALUE = ""

SP_SERVICE_UUID = ""
SP_SERVICE_AGREEMENT_UUID = ""
SP_MUNICIPALITY_UUID = ""
SP_SYSTEM_UUID = ""
SP_CERTIFICATE_PATH = ""

PROD_MODE = False

#USER_SETTINGS_DB_NAME = 'mora'
#USER_SETTINGS_DB_USER = 'mora'
#USER_SETTINGS_DB_PASSWORD = 'mora'
#USER_SETTINGS_DB_HOST = 'localhost'
USER_SETTINGS_DB_FILE = '/tmp/usersettings.db'

QUERY_EXPORT_DIR = ''


_util.update_config(globals(), CONFIG_FILE)
