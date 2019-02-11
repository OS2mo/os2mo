#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import re

from . import base
from ... import exceptions


class EANAddressHandler(base.AddressHandler):
    scope = 'EAN'
    prefix = 'urn:magenta.dk:ean:'

    @classmethod
    def validate_value(cls, value):
        """EANs are 13 digits"""
        if not re.match(r'\d{13}', value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EAN(
                value=value,
            )
