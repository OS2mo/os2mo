# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re

from ... import exceptions
from ..validation.validator import forceable
from . import base


class PhoneAddressHandler(base.AddressHandler):
    scope = "PHONE"
    prefix = "urn:magenta.dk:telefon:"

    @property
    def href(self):
        return f"tel:{self._value}"

    @staticmethod
    @forceable
    async def validate_value(value):
        """Phone number is only digits, optionally with country code"""
        if not re.match(r"^\+?\d+$", value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_PHONE(
                value=value,
            )
