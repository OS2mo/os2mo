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

    def __init__(self, value, visibility):
        self.visibility = visibility

        super().__init__(value)

    @classmethod
    def from_effect(cls, effect):
        """Initialize handler from LoRa object"""
        # Cut off the prefix
        urn = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('urn')
        value = urn[len(cls.prefix):]

        visibility_field = mapping.VISIBILITY_FIELD(effect)
        visibility = visibility_field[0]['uuid'] if visibility_field else None

        return cls(value, visibility)

    @classmethod
    def from_request(cls, request):
        value = util.checked_get(request, mapping.VALUE, "", required=True)
        visibility = util.get_mapping_uuid(request, mapping.VISIBILITY)

        return cls(value, visibility)

    @property
    def href(self):
        return 'tel:{}'.format(self._value)

    def get_lora_properties(self):
        properties = super().get_lora_properties()
        if self.visibility:
            properties.append(
                {
                    'objekttype': 'synlighed',
                    'uuid': self.visibility
                }
            )
        return properties

    def _get_mo_properties(self):
        properties = super()._get_mo_properties()
        if self.visibility:
            c = lora.Connector()
            properties.update({
                mapping.VISIBILITY: facet.get_one_class(c, self.visibility)
            })
        return properties

    @staticmethod
    @forceable
    def validate_value(value):
        """Phone number is only digits, optionally with country code"""
        if not re.match(r'^\+?\d+$', value):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_PHONE(
                value=value,
            )
