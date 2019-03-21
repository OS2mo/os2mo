#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from ... import util
from ... import mapping
from . import base


class TextAddressHandler(base.AddressHandler):
    scope = 'TEXT'
    prefix = 'urn:text:'

    @property
    def urn(self):
        return self.prefix + util.urnquote(self.value)

    @classmethod
    def from_effect(cls, effect):
        """Initialize handler from LoRa object"""
        # Cut off the prefix
        urn = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('urn')
        quoted_value = urn[len(cls.prefix):]
        value = util.urnunquote(quoted_value)
        return cls(value)

    @staticmethod
    def validate_value(value):
        """Text value can be whatever"""
        pass
