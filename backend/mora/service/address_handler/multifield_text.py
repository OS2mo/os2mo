# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from more_itertools import first

from ... import mapping
from ... import util
from . import base


def name(value1, value2) -> str:
    # value2 is more than empty spaces
    if not value2 or not value2.strip():
        return value1
    return f"{value1} :: {value2}"


class MultifieldTextAddressHandler(base.AddressHandler):
    scope = "MULTIFIELD_TEXT"
    prefix = "urn:multifield_text:"
    prefix2 = "urn:multifield_text2:"

    @property
    def name(self):
        return name(self._value, self._value2)

    @staticmethod
    def _value_from_effect(effect, prefix: str):
        def unquote_value(urn):
            quoted_value = urn[len(prefix) :]
            return util.urnunquote(quoted_value)

        urns = [x.get("urn") for x in mapping.ADDRESSES_FIELD(effect)]
        urns = filter(lambda urn: prefix in urn, urns)
        urns = map(unquote_value, urns)
        return first(urns, None)

    @classmethod
    async def from_effect(cls, effect):
        """Initialize handler from LoRa object"""
        # Cut off the prefix
        value = cls._value_from_effect(effect, cls.prefix)
        value2 = cls._value_from_effect(effect, cls.prefix2)

        visibility_field = mapping.VISIBILITY_FIELD(effect)
        visibility = visibility_field[0]["uuid"] if visibility_field else None
        return cls(value, visibility, value2=value2)

    @staticmethod
    async def validate_value(value):
        """Text value is not restricted."""
        pass

    @classmethod
    async def from_request(cls, request):
        value = util.checked_get(request, mapping.VALUE, "", required=True)
        value2 = util.checked_get(request, mapping.VALUE2, "", required=False)
        await cls.validate_value(value)
        await cls.validate_value(value2)

        visibility = util.get_mapping_uuid(request, mapping.VISIBILITY, required=False)

        return cls(value, visibility, value2=value2)

    def get_lora_address(self):
        """
        Get a LoRa object fragment for the address

        Example::

          {
            'objekttype': 'PHONE',
            'urn': 'urn:magenta.dk:telefon:+4512345678'
          }
        """
        return [
            {
                "objekttype": self.scope,
                "urn": prefix + util.urnquote(value),
            }
            for (prefix, value) in (
                (self.prefix, self._value),
                (self.prefix2, self._value2),
            )
        ]
