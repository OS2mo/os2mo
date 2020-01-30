# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import re

from . import base
from ..validation.validator import forceable
from ... import exceptions


class PNumberAddressHandler(base.AddressHandler):
    scope = 'PNUMBER'
    prefix = 'urn:dk:cvr:produktionsenhed:'

    @staticmethod
    @forceable
    def validate_value(value):
        """P-numbers are 10 digits"""
        if not re.match(r'^\d{10}$', value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_PNUMBER(
                value=value,
            )
