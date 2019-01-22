from ... import util
from ... import mapping
from . import base


class TextAddressHandler(base.AddressHandler):
    scope = 'TEXT'
    prefix = 'urn:text:'

    def get_urn(self):
        return self.prefix + util.urnquote(self.value)

    @classmethod
    def from_effect(cls, effect):
        """Initialize handler from LoRa object"""
        # Cut off the prefix
        urn = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('urn')
        quoted_value = urn[len(cls.prefix):]
        value = util.urnunquote(quoted_value)
        return cls(value)
