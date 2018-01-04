#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from os import path as _path

from . import util as _util

BASE_DIR = _path.dirname(_path.dirname(_path.abspath(__file__)))
CONFIG_FILE = _path.join(BASE_DIR, 'config', 'mora.json')

LORA_URL = 'http://mox.lxc/'
CA_BUNDLE = None

SAML_IDP_TYPE = 'wso2'
SAML_IDP_URL = None
SAML_ENTITY_ID = 'localhost'
SAML_IDP_INSECURE = True

_util.update_config(globals(), CONFIG_FILE)
