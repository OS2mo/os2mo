#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import re

from . import base
from .. import facet
from ..validation.validator import forceable
from ... import exceptions
from ... import lora
from ... import mapping
from ... import util


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
