# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator
from uuid import UUID

from aiohttp import ClientResponseError
from fastramqpi.os2mo_dar_client import AsyncDARClient
from starlette_context import context
from starlette_context import request_cycle_context
from strawberry.dataloader import DataLoader
from structlog import get_logger

from mora.graphapi.middleware import is_graphql

from ... import config
from ... import exceptions
from ..validation.validator import forceable
from . import base

NOT_FOUND = "Ukendt"

logger = get_logger()


def open_street_map_href_from_dar_object(address_object) -> str | None:
    if not ("x" in address_object and "y" in address_object):  # pragma: no cover
        return None
    x, y = address_object["x"], address_object["y"]
    return f"https://www.openstreetmap.org/?mlon={x}&mlat={y}&zoom=16"


def name_from_dar_object(address_object) -> str:
    if address_object is None:
        return NOT_FOUND
    return "".join(DARAddressHandler._address_string_chunks(address_object))


async def load_addresses(keys: list[UUID]) -> list[dict | None]:
    adarclient = AsyncDARClient(timeout=120)
    async with adarclient:
        try:
            addresses, _ = await adarclient.fetch(set(keys))
        except ClientResponseError as exc:
            logger.exception("address lookup failed", exc=exc)
            return [None for _ in keys]
    return list(map(addresses.get, keys))


_MIDDLEWARE_KEY = "dar_loader"


async def dar_loader_context() -> AsyncIterator[None]:
    data = {**context, _MIDDLEWARE_KEY: DataLoader(load_fn=load_addresses)}
    with request_cycle_context(data):
        yield


class DARAddressHandler(base.AddressHandler):
    scope = "DAR"
    prefix = "urn:dar:"

    @classmethod
    async def from_effect(cls, effect):
        """
        Initialize handler from LoRa object

        If the saved address fails lookup in DAR for whatever reason, handle
        gracefully and return _some_ kind of result
        """
        # Cut off the prefix
        handler = await super().from_effect(effect)
        if is_graphql():
            # Return early if we're doing GraphQL things!
            handler._name = None
            handler._href = None
            return handler

        if not config.get_settings().enable_dar:  # pragma: no cover
            handler._name = None
            handler._href = None
            return handler

        dar_loader = context["dar_loader"]
        address_object = await dar_loader.load(UUID(handler.value))
        if address_object is None:
            logger.warning("address lookup failed", handler_value=handler.value)
            handler._href = None
        else:
            handler._href = open_street_map_href_from_dar_object(address_object)
        handler._name = name_from_dar_object(address_object)

        return handler

    @classmethod
    async def from_request(cls, request):
        """
        Initialize handler from MO object

        If lookup in DAR fails, this will raise an exception as we do not want
        to save an invalid object to LoRa.
        This lookup can be circumvented if the 'force' flag is used.
        """
        handler = await super().from_request(request)
        handler._href = None
        handler._name = handler._value
        return handler

    @property
    def name(self):
        return self._name

    @property
    def href(self):
        return self._href

    @staticmethod
    def _address_string_chunks(addr):
        # loosely inspired by 'adressebetegnelse' in apiSpecification/util.js
        # from https://github.com/DanmarksAdresser/Dawa/

        yield addr["vejnavn"]

        if addr.get("husnr") is not None:
            yield " "
            yield addr["husnr"]

        if addr.get("etage") is not None or addr.get("dør") is not None:
            yield ","

        if addr.get("etage") is not None:
            yield " "
            yield addr["etage"]
            yield "."

        if addr.get("dør") is not None:  # pragma: no cover
            yield " "
            yield addr["dør"]

        yield ", "

        if addr.get("supplerendebynavn") is not None:  # pragma: no cover
            yield addr["supplerendebynavn"]
            yield ", "

        yield addr["postnr"]
        yield " "
        yield addr["postnrnavn"]

    @staticmethod
    @forceable
    async def validate_value(value):
        """Values should be UUID in DAR"""
        dar_loader = context["dar_loader"]
        try:
            address_object = await dar_loader.load(UUID(value))
            if address_object is None:
                raise LookupError(f"no such address {value!r}")
        except (ValueError, LookupError):
            exceptions.ErrorCodes.V_INVALID_ADDRESS_DAR(value=value)
