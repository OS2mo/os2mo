# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from __future__ import generator_stop

import math

import asyncio
import logging
import re
import typing
import uuid
from asyncio import create_task, gather
from enum import Enum, unique
from functools import partial
from itertools import starmap

import lora_utils
from more_itertools import chunked

import mora.async_util
from . import exceptions
from . import settings
from . import util

logger = logging.getLogger(__name__)


@unique
class LoraObjectType(Enum):
    org = 'organisation/organisation'
    org_unit = 'organisation/organisationenhed'
    org_func = 'organisation/organisationfunktion'
    user = 'organisation/bruger'
    it_system = 'organisation/itsystem'
    class_ = 'klassifikation/klasse'
    facet = 'klassifikation/facet'
    classification = 'klassifikation/klassifikation'


def raise_on_status(status_code: int, msg,
                    cause: typing.Optional = None) -> typing.NoReturn:
    """
    unified raising error codes

    @param status_code: status code from response (http status code)
    @param msg: something informative
    @param cause: same
    @return:
    """
    # Check status code 400 against this regex to detect "no-op" data updates.
    noop_pattern = re.compile(
        r"Aborted updating \w+ with id \[.*\] as the given data, does not "
        r"give raise to a new registration"
    )

    if status_code == 400:
        # If LoRa returns HTTP status code 400, first check if the error
        # reported indicates a "no-op" change (no data was actually changed in
        # the update.)
        if noop_pattern.search(msg):
            logger.info(
                "detected empty change, not raising E_INVALID_INPUT\n"
                "msg=%r",
                msg
            )
        else:
            exceptions.ErrorCodes.E_INVALID_INPUT(message=msg, cause=cause)
    elif status_code == 401:
        exceptions.ErrorCodes.E_UNAUTHORIZED(message=msg, cause=cause)
    elif status_code == 403:
        exceptions.ErrorCodes.E_FORBIDDEN(message=msg, cause=cause)
    else:
        exceptions.ErrorCodes.E_UNKNOWN(message=msg, cause=cause)


async def _check_response(r):
    if 400 <= r.status < 600:  # equivalent to requests.response.ok
        try:
            cause = await r.json()
            msg = cause['message']
        except (ValueError, KeyError):
            cause = None
            msg = await r.text()

        raise_on_status(status_code=r.status, msg=msg, cause=cause)

    return r


def bool_to_str(value):
    """
    just to converting bools to str, even if nested in an other structure
    @param value:
    @return:
    """
    if isinstance(value, bool):
        return str(value)
    elif isinstance(value, list) or isinstance(value, set):
        return list(map(bool_to_str, value))
    elif isinstance(value, int) or isinstance(value, str):
        return value
    else:
        raise TypeError("Unknown type in bool_to_str", type(value))


def param_bools_to_strings(params: typing.Dict[
    typing.Any, typing.Union[bool, typing.List, typing.Set, str, int]]) -> \
    typing.Dict[typing.Any,
                typing.Union[str, int, typing.List]]:
    """
    converts requests-compatible params to aiohttp-compatible params

    @param params: dict of parameters
    @return:
    """
    ret = {key: bool_to_str(value) for key, value in params.items()
           if value is not None}
    return ret


class Connector:

    def __init__(self, **defaults):
        self.__validity = defaults.pop('validity', None) or 'present'

        self.now = util.parsedatetime(
            defaults.pop('effective_date', None) or util.now(),
        )

        if self.__validity == 'past':
            self.start = util.NEGATIVE_INFINITY
            self.end = self.now

        elif self.__validity == 'future':
            self.start = self.now
            self.end = util.POSITIVE_INFINITY

        elif self.__validity == 'present':
            # we should probably use 'virkningstid' but that means we
            # have to override each and every single invocation of the
            # accessors later on
            if 'virkningfra' in defaults:
                self.start = self.now = util.parsedatetime(
                    defaults.pop('virkningfra'),
                )
            else:
                self.start = self.now

            if 'virkningtil' in defaults:
                self.end = util.parsedatetime(defaults.pop('virkningtil'))
            else:
                self.end = self.start + util.MINIMAL_INTERVAL

        else:
            exceptions.ErrorCodes.V_INVALID_VALIDITY(validity=self.__validity)

        defaults.update(
            virkningfra=util.to_lora_time(self.start),
            virkningtil=util.to_lora_time(self.end),
            konsolider=True,
        )

        self.__defaults = defaults
        self.__scopes = {}

    @property
    def defaults(self):
        return self.__defaults

    @property
    def validity(self):
        return self.__validity

    def is_range_relevant(self, start, end, effect):
        if self.validity == 'present':
            return util.do_ranges_overlap(self.start, self.end, start, end)
        else:
            return start > self.start and end <= self.end

    def scope(self, type_: LoraObjectType) -> 'Scope':
        if type_ in self.__scopes:
            return self.__scopes[type_]
        return self.__scopes.setdefault(type_, Scope(self, type_.value))

    @property
    def organisation(self) -> 'Scope':
        return self.scope(LoraObjectType.org)

    @property
    def organisationenhed(self) -> 'Scope':
        return self.scope(LoraObjectType.org_unit)

    @property
    def organisationfunktion(self) -> 'Scope':
        return self.scope(LoraObjectType.org_func)

    @property
    def bruger(self) -> 'Scope':
        return self.scope(LoraObjectType.user)

    @property
    def itsystem(self) -> 'Scope':
        return self.scope(LoraObjectType.it_system)

    @property
    def klasse(self) -> 'Scope':
        return self.scope(LoraObjectType.class_)

    @property
    def facet(self) -> 'Scope':
        return self.scope(LoraObjectType.facet)

    @property
    def klassifikation(self) -> 'Scope':
        return self.scope(LoraObjectType.classification)


class Scope:
    def __init__(self, connector, path):
        self.connector = connector
        self.path = path

    @property
    def base_path(self):
        return settings.LORA_URL + self.path

    async def fetch(self, **params):
        async with mora.async_util.async_session(
        ).get(self.base_path,
              params=param_bools_to_strings(
                  {**self.connector.defaults, **params})) as response:
            await _check_response(response)

            try:
                ret = (await response.json())['results'][0]
                return ret
            except IndexError:
                return []

    async def get_all(self, **params):
        """Perform a search on given params and return the result.

        As we perform a search in LoRa, using 'uuid' as a parameter is not supported,
        as LoRa will raise in error.

        Currently we hardcode the use of 'list' to return items from the search,
        so supplying 'list' as a parameter is not supported.

        Returns an iterator of tuples (obj_id, obj) of all matches.
        """
        ass_msg = "'{}' is not a supported parameter for 'get_all'{}."
        assert "list" not in params, ass_msg.format("list", ", implicitly set")
        assert "uuid" not in params, ass_msg.format("uuid", ", use 'get_all_by_uuid'")
        assert "start" not in params, ass_msg.format("start", ", use 'paged_get'")
        assert "limit" not in params, ass_msg.format("limit", ", use 'paged_get'")

        wantregs = not params.keys().isdisjoint(
            {'registreretfra', 'registrerettil'}
        )
        response = await self.fetch(**dict(params), list=1)

        def gen():
            for d in response:
                yield d['id'], (d['registreringer'] if wantregs
                                else d['registreringer'][0])

        return gen()

    async def get_all_by_uuid(self,
                              uuids: typing.Union[typing.List, typing.Set]
                              ) -> typing.Iterable[typing.Tuple[str,
                                                                typing.Dict[
                                                                    typing.Any,
                                                                    typing.Any]]]:

        """Get a list of objects by their UUIDs.

        Returns an iterator of tuples (obj_id, obj) of all matches.
        """

        # There is currently an issue in uvicorn related to long request URLs
        # https://github.com/encode/uvicorn/issues/344
        # Until it is fixed we need to enfore a max length of requests

        # I haven't been able to determine exactly how long requests can be
        # The following value is based purely on experimentation
        max_uuid_part_length = 5000
        # length of uuid + '?uuid=' = 42
        uuids_per_chunk = math.floor(max_uuid_part_length / 42)
        uuid_chunks = chunked(uuids, uuids_per_chunk)

        # # heuristic, depends on who is serving this app
        # n_chunk_target = multiprocessing.cpu_count() * 2 + 1
        # length = len(uuids)
        # min_size = 20
        # n_chunks = n_chunk_target
        # if length < min_size:
        #     n_chunks = 1
        #
        # # chunk to get some 'fake' performance by parallelize
        # uuid_chunks = divide(n_chunks, uuids)

        need_flat = await gather(*[create_task(self.fetch(uuid=list(ch)))
                                   for ch in uuid_chunks])
        ret = [x for chunk in need_flat for x in chunk]

        # ret = await self.fetch(uuid=uuids)

        # funny looking, but keeps api backwards compatible (ie avoiding 'async for')
        def gen():
            for d in ret:
                yield d['id'], (d['registreringer'][0])

        return gen()

    async def paged_get(self,
                        func: typing.Callable[['Connector', typing.Any, typing.Any],
                                              typing.Union[
                                                  typing.Any, typing.Coroutine]], *,
                        start=0, limit=0,
                        uuid_filters=None,
                        **params):
        """Perform a search on given params, filter and return the result.

        :code:`func` is a function from (lora-connector, obj_id, obj) to
        :code:`item-type`.

        :code:`uuid_filters` is a list of functions from uuid to bool, where
        the uuid will be kept assuming the returned bool is truthy.

        Returns paged dict with 3 keys: 'total', 'offset' and 'items', where:
            'total' is the total number of matches found.
            'offset' is the offset into 'total' (for pagination).
            'items' is a list of :code:`item-type` items.
        """
        uuid_filters = uuid_filters or []
        # Fetch all uuids matching search params and filter with uuid_filters
        uuids = await self.fetch(**params)
        for uuid_filter in uuid_filters:
            uuids = filter(uuid_filter, uuids)
        # Sort to ensure consistent order, as LoRa does not seem to do that
        uuids = sorted(list(uuids))
        total = len(uuids)
        # Offset by slicing off the start
        uuids = uuids[start:]
        # Limit by slicing off the end
        if limit > 0:
            uuids = uuids[:limit]
        # Lookup objects by uuid, and build objects using func
        obj_iter = await self.get_all_by_uuid(uuids)
        if asyncio.iscoroutinefunction(func):
            obj_iter = await gather(*[func(self.connector, *tup) for tup in obj_iter])
        else:
            obj_iter = starmap(partial(func, self.connector), obj_iter)

        return {
            'total': total,
            'offset': start,
            'items': list(obj_iter)
        }

    async def get(self, uuid, **params):
        d = await self.fetch(uuid=str(uuid), **params)

        if not d or not d[0]:
            return None

        registrations = d[0]['registreringer']

        assert len(d) == 1

        if params.keys() & {'registreretfra', 'registrerettil'}:
            return registrations
        else:
            assert len(registrations) == 1

            return registrations[0]

    async def create(self, obj, uuid=None):
        if uuid:
            async with mora.async_util.async_session(
            ).put('{}/{}'.format(self.base_path, uuid),
                  json=obj) as r:

                async with r:
                    await _check_response(r)
                    return (await r.json())['uuid']
        else:
            async with mora.async_util.async_session(
            ).post(self.base_path,
                   json=obj) as r:
                await _check_response(r)
                return (await r.json())['uuid']

    async def delete(self, uuid):
        async with mora.async_util.async_session(
        ).delete('{}/{}'.format(self.base_path, uuid)) as response:
            await _check_response(response)

    async def update(self, obj, uuid):
        async with mora.async_util.async_session(
        ).patch('{}/{}'.format(self.base_path, uuid), json=obj) as response:
            await _check_response(response)
            return (await response.json()).get('uuid', uuid)

    async def get_effects(self, obj, relevant, also=None, **params):
        reg = (
            await self.get(obj, **params)
            if isinstance(obj, (str, uuid.UUID))
            else obj
        )

        if not reg:
            return

        effects = list(lora_utils.get_effects(reg, relevant, also))

        return filter(
            lambda a: self.connector.is_range_relevant(*a),
            effects,
        )


async def get_version():
    async with mora.async_util.async_session(
    ).get(settings.LORA_URL + "version") as response:
        try:
            return (await response.json())["lora_version"]
        except ValueError:
            return "Could not find lora version: %s" % await response.text()
