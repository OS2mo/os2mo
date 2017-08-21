#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

from . import util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

LORA_URL = 'http://mox/'

SAML_IDP_TYPE = 'wso2'
SAML_IDP_URL = None
SAML_ENTITY_ID = 'localhost'
SAML_IDP_INSECURE = True

util.update_config(globals(), CONFIG_FILE)
