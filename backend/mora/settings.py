#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import json
from os import path as _path

from . import util as _util

BASE_DIR = _path.dirname(_path.dirname(_path.abspath(__file__)))
CONFIG_FILE = _path.join(BASE_DIR, '..', 'setup', 'mora.json')

MAX_REQUEST_LENGTH = 4096
DEFAULT_PAGE_SIZE = 2000

LORA_URL = 'http://localhost:8080/'
CA_BUNDLE = None

AUTH = 'token'  # 'sso' or 'token'

SESSION_FILE_DIR = '/tmp'

# Token auth config
SAML_IDP_TYPE = 'wso2'
SAML_IDP_URL = None
SAML_ENTITY_ID = 'localhost'
SAML_IDP_INSECURE = False

# SSO config
SSO_SAML_METADATA_URL = '/url/to/sso/metadata'
SSO_SAML_USERNAME_ATTR = ''
SAML_KEY_FILE = None
SAML_CERT_FILE = None
SAML_AUTHN_REQUESTS_SIGNED = False

SP_SERVICE_UUID = ""
SP_SERVICE_AGREEMENT_UUID = ""
SP_MUNICIPALITY_UUID = ""
SP_SYSTEM_UUID = ""
SP_CERTIFICATE_PATH = ""

PROD_MODE = False

try:
    with open('backend/mora/user_settings.json') as f:
        user_settings = json.load(f)
except FileNotFoundError:  # Defaults
    user_settings = {'orgunit': {'show_location': True,
                                 'show_bvn': False,
                                 'show_roles': True}
                     }

_util.update_config(globals(), CONFIG_FILE)
