# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pydantic import EmailStr
from pydantic import ValidationError
from pydantic import parse_obj_as

from ... import exceptions
from ..validation.validator import forceable
from . import base


class EmailAddressHandler(base.AddressHandler):
    scope = "EMAIL"
    prefix = "urn:mailto:"

    @property
    def href(self) -> str:
        return f"mailto:{self.value}"

    @staticmethod
    @forceable
    async def validate_value(value):
        """Ensure that value is correct email"""
        try:
            parse_obj_as(EmailStr, value)
        except ValidationError:
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EMAIL(
                value=value,
            )
