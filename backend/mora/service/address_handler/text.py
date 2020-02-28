# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

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

        visibility_field = mapping.VISIBILITY_FIELD(effect)
        visibility = visibility_field[0]['uuid'] if visibility_field else None

        return cls(value, visibility)

    @staticmethod
    def validate_value(value):
        """Text value can be whatever"""
        pass
