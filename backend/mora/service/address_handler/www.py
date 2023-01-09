# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pydantic import AnyHttpUrl
from pydantic import parse_obj_as
from pydantic import ValidationError

from . import base
from ... import exceptions
from ..validation.validator import forceable


class WWWAddressHandler(base.AddressHandler):
    scope = "WWW"
    prefix = "urn:magenta.dk:www:"

    @staticmethod
    @forceable
    async def validate_value(value):
        """Ensure value is correct URL"""
        try:
            parse_obj_as(AnyHttpUrl, value)
        except ValidationError:
            exceptions.ErrorCodes.V_INVALID_ADDRESS_WWW(
                value=value,
            )
