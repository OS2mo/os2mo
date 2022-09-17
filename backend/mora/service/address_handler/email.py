# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from pydantic import EmailStr
from pydantic import parse_obj_as
from pydantic import ValidationError

from . import base
from ... import exceptions
from ..validation.validator import forceable


class EmailAddressHandler(base.AddressHandler):
    scope = "EMAIL"
    prefix = "urn:mailto:"

    @property
    def href(self):
        return "mailto:{}".format(self.value)

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
