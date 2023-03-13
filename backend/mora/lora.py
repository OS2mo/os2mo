# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import json
import re
import uuid
from asyncio import gather
from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Container
from collections.abc import Coroutine
from collections.abc import ItemsView
from collections.abc import Iterable
from datetime import date
from datetime import datetime
from datetime import time
from enum import Enum
from enum import unique
from functools import partial
from itertools import starmap
from typing import Any
from typing import Literal
from typing import NoReturn
from typing import Optional
from typing import TypeVar

import httpx
import lora_utils
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from strawberry.dataloader import DataLoader
from structlog import get_logger

from . import config
from . import exceptions
from . import util
from .graphapi.middleware import is_graphql
from .util import DEFAULT_TIMEZONE
from .util import from_iso_time
from oio_rest.config import get_settings as get_lora_settings


T = TypeVar("T")
V = TypeVar("V")
ValidityLiteral = Literal["past", "present", "future"]


logger = get_logger()
settings = config.get_settings()


async def create_lora_client(app: FastAPI | None = None) -> httpx.AsyncClient:
    """Return lora client.

    IThis transparently sends requests to the internal LoRa ASGI app.
    """
    return AsyncClient(
        app=app,
        base_url="http://localhost/lora/",
        timeout=config.get_settings().httpx_timeout,
    )


# Singleton LoRa client:
client = None


def registration_changed_since(reg: dict[str, Any], since: datetime) -> bool:
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
    response: list[dict[str, Any]],
    wantregs: bool,
    changed_since: datetime | None = None,
) -> Iterable[tuple[str, list[dict[str, Any]] | dict[str, Any]]]:
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


def raise_on_status(status_code: int, msg, cause: Optional = None) -> NoReturn:
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
                "detected empty change, not raising E_INVALID_INPUT", message=msg
            )
        else:
            exceptions.ErrorCodes.E_INVALID_INPUT(message=msg, cause=cause)
    elif status_code == 401:
        exceptions.ErrorCodes.E_UNAUTHORIZED(message=msg, cause=cause)
    elif status_code == 403:
        exceptions.ErrorCodes.E_FORBIDDEN(message=msg, cause=cause)
    elif status_code == 404:
        exceptions.ErrorCodes.E_NOT_FOUND(message=msg, cause=cause)
    else:
        exceptions.ErrorCodes.E_UNKNOWN(message=msg, cause=cause)


async def _check_response(r: httpx.Response) -> httpx.Response:
    if 400 <= r.status_code < 600:
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
    return value


def exotics_to_str(value):
    """
    just to converting "exotic"-types to str, even if nested in an other structure
    @param value:
    @return:
    """
    if isinstance(value, (bool, uuid.UUID)):
        return str(value)
    elif isinstance(value, (list, set)):
        return list(map(exotics_to_str, value))
    elif isinstance(value, (int, str)):
        return value
    raise TypeError("Unknown type in exotics_to_str", type(value))


def param_exotics_to_strings(
    params: dict[T, bool | list | set | str | int | uuid.UUID]
) -> dict[T, str | int | list]:
    """
    converts requests-compatible (and more) params to aiohttp-compatible params

    @param params: dict of parameters
    @return:
    """
    ret = {
        key: exotics_to_str(value) for key, value in params.items() if value is not None
    }
    return ret


def validity_tuple(
    validity: ValidityLiteral, now: date | datetime = None
) -> tuple[datetime, datetime]:
    """Return (start, end) tuple of datetimes for Lora."""
    if now is None:
        now = util.parsedatetime(util.now())

    # NOTE: We must explicitly convert date to datetime since the minimum resolution of date is
    # one day, which means that the addition of timedelta(microseconds=1) later will silently
    # be ignored.
    if type(now) is date:
        now = datetime.combine(now, time.min)

    if validity == "past":
        return util.NEGATIVE_INFINITY, now

    if validity == "present":
        return now, now + util.MINIMAL_INTERVAL

    if validity == "future":
        return now, util.POSITIVE_INFINITY

    raise TypeError(
        f"Expected validity to be 'past', 'present' or 'future', but was {validity}"
    )


class Connector:
    def __init__(self, **defaults):
        self.__validity = defaults.pop("validity", None) or "present"

        self.now = util.parsedatetime(
            defaults.pop("effective_date", None) or util.now(),
        )

        if self.__validity == "present":
            # we should probably use 'virkningstid' but that means we
            # have to override each and every single invocation of the
            # accessors later on
            if "virkningfra" in defaults:
                self.now = util.parsedatetime(defaults.pop("virkningfra"))

        try:
            self.start, self.end = validity_tuple(self.__validity, now=self.now)
        except TypeError:
            exceptions.ErrorCodes.V_INVALID_VALIDITY(validity=self.__validity)

        if self.__validity == "present" and "virkningtil" in defaults:
            self.end = util.parsedatetime(defaults.pop("virkningtil"))

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
        if self.validity == "present":
            return util.do_ranges_overlap(self.start, self.end, start, end)
        return start > self.start and end <= self.end

    def scope(self, type_: LoraObjectType) -> "Scope":
        if type_ in self.__scopes:
            return self.__scopes[type_]
        return self.__scopes.setdefault(type_, Scope(self, type_.value))

    @property
    def organisation(self) -> "Scope":
        return self.scope(LoraObjectType.org)

    @property
    def organisationenhed(self) -> "Scope":
        return self.scope(LoraObjectType.org_unit)

    @property
    def organisationfunktion(self) -> "Scope":
        return self.scope(LoraObjectType.org_func)

    @property
    def bruger(self) -> "Scope":
        return self.scope(LoraObjectType.user)

    @property
    def itsystem(self) -> "Scope":
        return self.scope(LoraObjectType.it_system)

    @property
    def klasse(self) -> "Scope":
        return self.scope(LoraObjectType.class_)

    @property
    def facet(self) -> "Scope":
        return self.scope(LoraObjectType.facet)


def group_params(
    param_keys: tuple[T],
    params_list: list[tuple[frozenset[V]]],
) -> dict[T, set[V]]:
    """
    Transform parameters from
        (a, b)
    and
        [
            ({1}, {11}),
            ({2}, {22, 33}),
            ({3}, {33}),
        ]
    to
        {
            "a": {1, 2, 3},
            "b": {11, 22, 33},
        }
    with duplicates removed.
    """
    grouped_params = defaultdict(set)
    for params in params_list:
        for key, values in zip(param_keys, params):
            grouped_params[key].update(values)
    return dict(grouped_params)  # we don't want defaultdict behaviour returned


class ParameterValuesExtractor:
    @classmethod
    def get_key_value_items(
        cls, d: dict[str, Any], search_keys: Container[str]
    ) -> Iterable[tuple[str, Any]]:
        """
        Given a LoRa result (nested dict), extract the value(s) for each key in
        search_keys as (key,value)-pairs.
        """
        for path, value in cls.traverse(d.items()):
            if (key := cls.get_key_for_path(path)) in search_keys:
                yield key, value

    @classmethod
    def traverse(
        cls,
        items: Iterable[tuple[str, Any]] | ItemsView[str, Any],
        path: tuple = (),
    ):
        """
        Recursively traverse the given nested dictionary, yielding (path, leaf)-pairs,
        where 'path' is expressed as a tuple of path components. The input dictionary is
        accepted as (key,value)-pairs to more easily support both lists and dicts.
        """
        for key, value in items:
            p = path + (key,)
            if isinstance(value, dict):
                yield from cls.traverse(value.items(), path=p)
            elif isinstance(value, list):
                yield from cls.traverse(enumerate(value), path=p)
            else:
                yield p, value

    @classmethod
    def get_key_for_path(cls, path: Iterable[str | int]) -> str:
        """
        Given a path (a,b,c), extract the final relevant path component (c). Each path
        component can be either a string or integer, for a dict key or list index,
        respectively. The following augmentations are performed:
          - 'uuid' is used in place of 'id', as that is always the input parameter used.
          - If c is 'uuid' and under the 'relationer' path, the next *labeled* (i.e.
            string, not list index integer) parent is returned.
        """
        *prefixes, suffix = path
        if suffix == "id":
            suffix = "uuid"
        if suffix == "uuid" and "relationer" in prefixes:
            return next(p for p in reversed(prefixes) if isinstance(p, str))
        return suffix


class BaseScope:
    def __init__(self, connector, path):
        self.connector = connector
        self.path = path


class Scope(BaseScope):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaders: dict[tuple[str], DataLoader] = {}

    def load(self, **params: Any) -> Awaitable[list[dict]]:
        """
        Like fetch(), but utilises Strawberry DataLoader to bulk requests automatically.
        Unlike fetch(), we never return just a list of UUIDs, since full objects are
        fetched anyway to map the individual results back into the original load()s.
        load(**params) == fetch(**params, list=1)
        load(uuid=uuid) == fetch(uuid=uuid)
        """
        # Fetch directly if feature flag turned off, or if we won't be able to map the
        # results back to the call params, or if using GraphQL, since we really don't
        # need nested DataLoaders in our life right now.
        def has_validity_params():
            return not params.keys().isdisjoint(
                {
                    "validity",
                    "virkningfra",
                    "virkningtil",
                    "registreretfra",
                    "registrerettil",
                }
            )

        def has_arbitrary_rel():
            return not params.keys().isdisjoint({"vilkaarligattr", "vilkaarligrel"})

        def has_wildcards():
            return any("%" in v for v in params.values() if isinstance(v, str))

        if (
            not settings.bulked_fetch
            or is_graphql()
            or has_validity_params()
            or has_arbitrary_rel()
            or has_wildcards()
        ):
            extra_fetch_params = {}
            # LoRa requires a 'list' operation for anything other than 'uuid', but it
            # doesn't care about the value - only the presence of the key - so we have
            # to add the parameter in this roundabout way.
            if params.keys() != {"uuid"}:
                extra_fetch_params["list"] = True
            return self.fetch(**params, **extra_fetch_params)

        # Convert parameters to ensure we can map the results back to the load() calls.
        # Also removes None values, as they won't actually be sent to LoRa anyway.
        params = param_exotics_to_strings(params)

        # LoRa supports using 'bvn' as an alias for 'brugervendtnoegle', but it's easier
        # if we can assume that the input parameters correspond to the output data.
        if "bvn" in params:
            params["brugervendtnoegle"] = params.pop("bvn")

        # We need to ensure all parameter keys in a batch are equal to avoid over-
        # constraining the results of the calls with the fewest keys. Take for example a
        # fully dense database with objects (a,b) in the interval 1-4:
        # load(a=1)
        # load(a=2, b=[3,4])
        # => fetch(a=[1,2], b=[3,4])
        # => [(a=1,b=3), (a=1,b=4), (a=2,b=3), (a=2,b=4)]
        # I.e. (a=1,b=1) and (a=1,b=2) for load(a=1) are missing from the results.
        param_keys = tuple(params.keys())  # dict keys must be hashable
        loader = self.loaders.setdefault(
            param_keys,
            DataLoader(load_fn=partial(self._load_loads, param_keys)),
        )

        # Convert all parameter values to sets for uniform processing. We pass it on to
        # the Strawberry DataLoader as a tuple of frozensets because it needs to be
        # hashable to enable caching. We don't need to pass the keys since the
        # DataLoader is unique per key.
        def to_frozenset(value: Any) -> frozenset:
            if not isinstance(value, Iterable) or isinstance(value, str):
                value = (value,)
            return frozenset(value)

        return loader.load(tuple(to_frozenset(v) for v in params.values()))

    async def load_uuids(self, **params: str | Iterable) -> list[str]:
        """
        Like load(), but map results back into UUIDs.
        load_uuids(**params) == fetch(**params)
        """
        return [x["id"] for x in await self.load(**params)]

    async def _load_loads(
        self,
        param_keys: tuple[str],
        params_list: list[tuple[frozenset]],
    ) -> list[list[dict]]:
        """
        Called by the DataLoader once all the load() calls have been collected.
        Takes a list of arguments to the original load() calls, and must return a list
        of the same length, corresponding to the return value for each load().
        """
        # (a,b), [(1,2), (3,4)] -> {a: [1,2], b: [3,4]}
        grouped_params = group_params(param_keys, params_list)

        # Get the UUIDs of the objects we need to fully fetch
        only_uuids = grouped_params.keys() == {"uuid"}
        if only_uuids:
            uuids = grouped_params["uuid"]
        else:
            uuid_results = await self.fetch(
                **grouped_params,
                list=True,
            )
            uuids = [r["id"] for r in uuid_results]

        # Fully fetch objects
        results = await self.fetch(uuid=uuids)

        # To associate each result object with the load() call(s!) that caused it, we
        # establish a mapping from each requested parameter (key,value)-pair into the
        # load() call(s) with that parameter pair. As an example, consider the calls:
        # X = load(a=1, b=[5,6])
        # Y = load(a=2, b=[6,7])
        # Z = load(a=3, b=6)
        # calls_for_params = {
        #   a: {1: {X}, 2: {Y}, 3: {Z}},
        #   b: {5: {X}, 6: {X,Y,Z}, 7: {Y}}
        # }
        calls_for_params = defaultdict(lambda: defaultdict(set))
        for i, params in enumerate(params_list):
            for key, values in zip(param_keys, params):
                for value in values:
                    calls_for_params[key][value].add(i)

        # To support multi-parameter load()s, a result object is associated with the
        # call if and only if its values matches the call parameters on *all* of the
        # parameter keys. Note that result objects may have multiple values for each
        # key. For example, consider the result object (a=[1,3], b=6]):
        # calls_for_params[a][1] => {X}
        # calls_for_params[a][3] => {Z}
        # calls_for_params[b][6] => {X,Y,Z}
        # Intersection(
        #   Union({X},{Z}),  # a
        #   Union({X,Y,Z}),  # b
        # ) = {X,Z}, therefore add the result to X and Z's results.
        # In the implementation, calls are referenced by their index in params_list.
        if not param_keys:
            # If the call parameters are empty, however, each call gets all objects
            # since none of them are filtering and we know the parameter keys are equal.
            return [results for _ in params_list]

        results_for_calls = list([] for _ in params_list)
        for result in results:
            # Find values in result for all parameter keys => [(a,1), (b,6), (a,3)]
            result_param_items = ParameterValuesExtractor.get_key_value_items(
                result, param_keys
            )
            # Collect calls matching ANY value from parameters => {a: {X,Z}, b: {X,Y,Z}}
            result_param_calls = defaultdict(set)
            for key, value in result_param_items:
                result_param_calls[key].update(calls_for_params[key][value])
            # Collapse into calls matching on ALL key,value parameters => {X,Z}
            result_calls = set.intersection(*result_param_calls.values())
            # Add this result to the matching calls => {X: [result], Y: [], Z: [result]}
            for call in result_calls:
                results_for_calls[call].append(result)

        return results_for_calls

    def encode_params(self, params: dict[str, Any]) -> bytes:
        return json.dumps(
            jsonable_encoder(param_exotics_to_strings({**params}))
        ).encode()

    async def fetch(self, **params):
        params = self.encode_params({**self.connector.defaults, **params})
        response = await client.request(
            method="GET",
            url=self.path,
            # We send the parameters as JSON through the body of the GET request to
            # allow arbitrarily many, as opposed to being limited by the length of a
            # URL if we were using query parameters.
            content=params,
        )
        await _check_response(response)
        try:
            ret = response.json()["results"][0]
            return ret
        except IndexError:
            return []

    async def get_all(self, changed_since: datetime | None = None, **params):
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

        response = await self.load(**params)
        wantregs = not params.keys().isdisjoint({"registreretfra", "registrerettil"})
        return filter_registrations(
            response=response, wantregs=wantregs, changed_since=changed_since
        )

    async def get_all_by_uuid(
        self,
        uuids: list | set,
        changed_since: datetime | None = None,
    ) -> Iterable[tuple[str, dict[Any, Any]]]:
        """
        Get a list of objects by their UUIDs.
        Returns an iterator of tuples (obj_id, obj) of all matches.
        """
        ret = await self.load(uuid=uuids)
        return filter_registrations(
            response=ret, wantregs=False, changed_since=changed_since
        )

    async def paged_get(
        self,
        func: Callable[
            ["Connector", Any, Any],
            Any | Coroutine,
        ],
        *,
        start=0,
        limit=0,
        uuid_filters=None,
        **params,
    ):
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

        return {"total": total, "offset": start, "items": list(obj_iter)}

    async def get(self, uuid, **params):
        d = await self.load(uuid=str(uuid), **params)

        if not d or not d[0]:
            return None

        registrations = d[0]["registreringer"]

        assert len(d) == 1

        if params.keys() & {"registreretfra", "registrerettil"}:
            return registrations
        else:
            assert len(registrations) == 1

            return registrations[0]

    async def create(self, obj, uuid=None):
        obj = uuid_to_str(obj)

        if uuid:
            uuid_path = f"{self.path}/{uuid}"
            response = await client.put(uuid_path, json=obj)
            await _check_response(response)
            return response.json()["uuid"]
        else:
            response = await client.post(self.path, json=obj)
            await _check_response(response)
            return response.json()["uuid"]

    async def delete(self, uuid: uuid.UUID) -> uuid.UUID:
        url = f"{self.path}/{uuid}"
        response = await client.delete(url)
        await _check_response(response)
        return response.json().get("uuid", uuid)

    async def update(self, obj, uuid):
        url = f"{self.path}/{uuid}"
        response = await client.patch(url, json=obj)
        if response.status_code == 404:
            logger.warning("could not update nonexistent LoRa object", url=url)
        else:
            await _check_response(response)
            return response.json().get("uuid", uuid)

    async def get_effects(self, obj, relevant, also=None, **params):
        reg = (
            await self.get(obj, **params) if isinstance(obj, (str, uuid.UUID)) else obj
        )

        if not reg:
            return

        effects = list(lora_utils.get_effects(reg, relevant, also))

        return filter(
            lambda a: self.connector.is_range_relevant(*a),  # noqa: FURB111
            effects,
        )


async def get_version():
    settings = get_lora_settings()
    return settings.commit_tag


class AutocompleteScope(BaseScope):
    def __init__(self, connector, path):
        self.connector = connector
        self.path = f"autocomplete/{path}"

    async def fetch(self, phrase: str, at: date | None = None, class_uuids: list[uuid.UUID] | None = None):
        params = {"phrase": phrase}
        if at:
            params["at"] = at.isoformat()

        if class_uuids:
            params["class_uuids"] = list(map(str, class_uuids))
        response = await client.get(url=self.path, params=params)
        await _check_response(response)
        return {"items": response.json()["results"]}
