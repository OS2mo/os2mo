#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import abc
import inspect

from ... import exceptions
from ... import mapping
from ... import util

ADDRESS_HANDLERS = {}


class _AddressHandlerMeta(abc.ABCMeta):
    """Metaclass for automatically registering handlers."""

    @staticmethod
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        if not inspect.isabstract(cls):
            cls._register()

        return cls


class AddressHandler(metaclass=_AddressHandlerMeta):
    __slots__ = 'scope', 'prefix', 'value'

    @classmethod
    def _register(cls):
        ADDRESS_HANDLERS[cls.scope] = cls

    def __init__(self, value):
        self.value = value

    @classmethod
    def from_effect(cls, effect):
        """Initialize handler from LoRa object"""
        # Cut off the prefix
        urn = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get('urn')
        value = urn[len(cls.prefix):]
        return cls(value)

    @classmethod
    def from_request(cls, request):
        """Initialize handler from MO object"""
        addrobj = util.checked_get(
            request, mapping.ADDRESS, {}, required=True)
        value = util.checked_get(addrobj, mapping.VALUE, "", required=True)
        return cls(value)

    def get_urn(self):
        return self.prefix + self.value

    def get_value(self):
        return self.value

    def get_pretty_value(self):
        return self.value

    def get_href(self):
        return None

    def get_lora_properties(self):
        return []

    def get_lora_address(self):
        return {
            'objekttype': self.scope,
            'urn': self.get_urn(),
        }

    def get_mo_properties(self):
        return {}

    def get_mo_address(self):
        return {
            mapping.HREF: self.get_href(),
            mapping.NAME: self.get_pretty_value(),
            mapping.VALUE: self.get_value()
        }


def get_handler_for_scope(scope: str) -> AddressHandler:
    handler = ADDRESS_HANDLERS.get(scope)
    if not handler:
        raise exceptions.ErrorCodes.E_INVALID_INPUT(
            'Invalid address scope type {}'.format(scope))
    return handler
