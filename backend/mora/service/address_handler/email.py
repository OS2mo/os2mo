#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import validators

from . import base
from ... import exceptions


class EmailAddressHandler(base.AddressHandler):
    scope = 'EMAIL'
    prefix = 'urn:mailto:'

    @property
    def href(self):
        return "mailto:{}".format(self.value)

    @classmethod
    def validate_value(cls, value):
        """Ensure that value is correct email"""
        if not validators.email(value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_EMAIL(
                value=value,
            )
