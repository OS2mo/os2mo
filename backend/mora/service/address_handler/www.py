#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import validators

from ... import exceptions

from . import base


class WWWAddressHandler(base.AddressHandler):
    scope = 'WWW'
    prefix = 'urn:magenta.dk:www:'

    @staticmethod
    def validate_value(value):
        """Ensure value is correct URL"""
        if not validators.url(value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_WWW(
                value=value,
            )
