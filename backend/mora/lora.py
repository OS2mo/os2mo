# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from __future__ import generator_stop

import asyncio
import math
import re
import typing
import uuid

import httpx
from structlog import get_logger
from asyncio import create_task, gather
from datetime import datetime
from enum import Enum, unique

from functools import partial
from itertools import starmap

import lora_utils
from more_itertools import chunked

from . import exceptions, config, util
from .util import DEFAULT_TIMEZONE, from_iso_time

logger = get_logger()


def registration_changed_since(
    reg: typing.Dict[str, typing.Any], since: datetime
) -> bool:
    from_time = reg.get("fratidspunkt", {}).get("tidsstempeldatotid", None)
    if from_time is None:
        raise ValueError(f"unexpected reg: {reg}")
    elif from_time == "infinity":
        return True
    elif from_time == "-infinity":
        return False

    # ensure timezone
    if not since.tzinfo:
        since = since.replace(tzinfo=DEFAULT_TIMEZONE)
    return from_iso_time(from_time) > since


def filter_registrations(
    response: typing.List[typing.Dict[str, typing.Any]], wantregs: bool,
    changed_since: typing.Optional[datetime] = None) -> typing.Iterable[
    typing.Tuple[str, typing.Union[
        typing.List[typing.Dict[str, typing.Any]], typing.Dict[str, typing.Any]]]]:
    """
    Helper, to filter registrations
    :param response: Registrations as received from LoRa
    :param wantregs: Determines whether one or more registrations are returned per uuid
    :param changed_since: datetime to filter by. If None, nothing is filtered
    :return: Iterable of (uuid, registration(s))
    """
    changed_since_filter = None
    if changed_since:
        changed_since_filter = partial(registration_changed_since, since=changed_since)

    # funny looking, but keeps api backwards compatible (ie avoiding 'async for')
    def gen():
        for d in response:
            regs = iter(d["registreringer"])
            if changed_since_filter is not None:
                regs = filter(changed_since_filter, regs)
            regs = list(regs)
            if regs:
                yield d["id"], (regs if wantregs else regs[0])

    return gen()


@unique
class LoraObjectType(Enum):
    org = "organisation/organisation"
    org_unit = "organisation/organisationenhed"
    org_func = "organisation/organisationfunktion"
    user = "organisation/bruger"
    it_system = "organisation/itsystem"
    class_ = "klassifikation/klasse"
    facet = "klassifikation/facet"
    classification = "klassifikation/klassifikation"


def raise_on_status(
    status_code: int, msg, cause: typing.Optional = None
) -> typing.NoReturn:
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
                "detected empty change, not raising E_INVALID_INPUT",
                message=msg
            )
        else:
            exceptions.ErrorCodes.E_INVALID_INPUT(message=msg, cause=cause)
    elif status_code == 401:
        exceptions.ErrorCodes.E_UNAUTHORIZED(message=msg, cause=cause)
    elif status_code == 403:
        exceptions.ErrorCodes.E_FORBIDDEN(message=msg, cause=cause)
    else:
        exceptions.ErrorCodes.E_UNKNOWN(message=msg, cause=cause)


def _check_response(r):
    if 400 <= r.status_code < 600:  # equivalent to requests.response.ok
        try:
            cause = r.json()
            msg = cause["message"]
        except (ValueError, KeyError):
            cause = None
            msg = r.text

        raise_on_status(status_code=r.status_code, msg=msg, cause=cause)

    return r


def uuid_to_str(value):
    """Used to convert UUIDs to str in nested structures"""
    if isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, dict):
        return {k: uuid_to_str(v) for k, v in value.items()}
    elif isinstance(value, list):
        return list(map(uuid_to_str, value))
    elif isinstance(value, set):
        return set(map(uuid_to_str, value))
    else:
        return value


def exotics_to_str(value):
    """
    just to converting "exotic"-types to str, even if nested in an other structure
    @param value:
    @return:
    """
    if isinstance(value, bool) or isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, list) or isinstance(value, set):
        return list(map(exotics_to_str, value))
    elif isinstance(value, int) or isinstance(value, str):
        return value
    else:
        raise TypeError("Unknown type in bool_to_str", type(value))


def param_exotics_to_strings(params: typing.Dict[
    typing.Any, typing.Union[bool, typing.List, typing.Set, str, int, uuid.UUID]]) -> \
    typing.Dict[typing.Any,
                typing.Union[str, int, typing.List]]:
    """
    converts requests-compatible (and more) params to aiohttp-compatible params

    @param params: dict of parameters
    @return:
    """
    ret = {key: exotics_to_str(value) for key, value in params.items()
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


class BaseScope:
    def __init__(self, connector, path):
        self.connector = connector
        self.path = path

    @property
    def base_path(self):
        return config.get_settings().lora_url + self.path


class Scope(BaseScope):
    async def fetch(self, **params):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_path,
                params=param_exotics_to_strings({**self.connector.defaults, **params})
            )
        _check_response(response)

        try:
            ret = response.json()['results'][0]
            return ret
        except IndexError:
            return []

    async def get_all(self, changed_since: typing.Optional[datetime] = None, **params):
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

        return filter_registrations(
            response=response, wantregs=wantregs, changed_since=changed_since
        )

    async def get_all_by_uuid(
        self,
        uuids: typing.Union[typing.List, typing.Set],
        changed_since: typing.Optional[datetime] = None,
    ) -> typing.Iterable[typing.Tuple[str, typing.Dict[typing.Any, typing.Any]]]:

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
        return filter_registrations(
            response=ret, wantregs=False, changed_since=changed_since
        )

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
        obj = uuid_to_str(obj)

        if uuid:
            async with httpx.AsyncClient() as client:
                r = await client.put(
                    '{}/{}'.format(self.base_path, uuid), json=obj)

            _check_response(r)
            return r.json()['uuid']
        else:
            async with httpx.AsyncClient() as client:
                r = await client.post(self.base_path, json=obj)
            _check_response(r)
            return r.json()['uuid']

    async def delete(self, uuid):
        async with httpx.AsyncClient() as client:
            response = await client.delete('{}/{}'.format(self.base_path, uuid))
        _check_response(response)

    async def update(self, obj, uuid):
        async with httpx.AsyncClient() as client:
            url = '{}/{}'.format(self.base_path, uuid)
            response = await client.patch(url, json=obj)
        if response.status_code == 404:
            logger.warning("could not update nonexistent LoRa object", url=url)
        else:
            _check_response(response)
            return response.json().get('uuid', uuid)

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
    async with httpx.AsyncClient() as client:
        response = await client.get(config.get_settings().lora_url + "version")
    try:
        return response.json()["lora_version"]
    except ValueError:
        return "Could not find lora version: %s" % response.text()


class AutocompleteScope(BaseScope):
    def __init__(self, connector, path):
        self.connector = connector
        self.path = f"autocomplete/{path}"

    async def fetch(self, phrase, class_uuids=None):
        params = {"phrase": phrase}
        if class_uuids:
            params["class_uuids"] = [str(uuid) for uuid in class_uuids]
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_path, params=params)
        _check_response(response)
        return {"items": response.json()["results"]}
