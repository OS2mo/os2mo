# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import re

from . import base
from ..validation.validator import forceable
from ... import exceptions


class EANAddressHandler(base.AddressHandler):
    scope = 'EAN'
    prefix = 'urn:magenta.dk:ean:'

    @staticmethod
    @forceable
    def validate_value(value):
        """EANs are 13 digits"""
        if not re.match(r'^\d{13}$', value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EAN(
                value=value,
            )
