# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re

from ... import exceptions
from ..validation.validator import forceable
from . import base


class EANAddressHandler(base.AddressHandler):
    scope = "EAN"
    prefix = "urn:magenta.dk:ean:"

    @staticmethod
    @forceable
    async def validate_value(value):
        """EANs are 13 digits"""
        if not re.match(r"^\d{13}$", value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EAN(
                value=value,
            )
