# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import validators

from . import base
from ..validation.validator import forceable
from ... import exceptions


class EmailAddressHandler(base.AddressHandler):
    scope = 'EMAIL'
    prefix = 'urn:mailto:'

    @property
    def href(self):
        return "mailto:{}".format(self.value)

    @staticmethod
    @forceable
    def validate_value(value):
        """Ensure that value is correct email"""
        if not validators.email(value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EMAIL(
                value=value,
            )
