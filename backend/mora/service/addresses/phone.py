#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import re

from . import base
from ... import mapping
from ... import util


class PhoneAddressHandler(base.AddressHandler):
    scope = 'PHONE'
    prefix = 'urn:magenta.dk:telefon:'

    def __init__(self, value, visibility):
        value = re.sub(r'\s+', '', value)
        if not value.startswith('+'):
            value = '+45' + value

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
        addrobj = util.checked_get(
            request, mapping.ADDRESS, {}, required=True)
        value = util.checked_get(addrobj, mapping.VALUE, "", required=True)
        visibility = util.get_mapping_uuid(request, mapping.VISIBILITY)

        return cls(value, visibility)

    def get_value(self):
        return self.value[3:]

    def get_href(self):
        return 'tel:{}'.format(self.get_pretty_value())

    def get_lora_properties(self):
        if self.visibility:
            return [
                {
                    'objekttype': 'synlighed',
                    'uuid': self.visibility
                }
            ]
        else:
            return super().get_lora_properties()

    def get_mo_properties(self):
        if self.visibility:
            return {
                mapping.VISIBILITY: {
                    'uuid': self.visibility
                }
            }
        else:
            return super().get_mo_properties()
