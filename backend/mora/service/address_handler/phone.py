# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import re

from . import base
from ..validation.validator import forceable
from ... import exceptions


class PhoneAddressHandler(base.AddressHandler):
    scope = 'PHONE'
    prefix = 'urn:magenta.dk:telefon:'

    @property
    def href(self):
        return 'tel:{}'.format(self._value)

    @staticmethod
    @forceable
    def validate_value(value):
        """Phone number is only digits, optionally with country code"""
        if not re.match(r'^\+?\d+$', value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_PHONE(
                value=value,
            )
