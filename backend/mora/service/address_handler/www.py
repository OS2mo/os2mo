# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import validators

from . import base
from ..validation.validator import forceable
from ... import exceptions


class WWWAddressHandler(base.AddressHandler):
    scope = 'WWW'
    prefix = 'urn:magenta.dk:www:'

    @staticmethod
    @forceable
    def validate_value(value):
        """Ensure value is correct URL"""
        if not validators.url(value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_WWW(
                value=value,
            )
