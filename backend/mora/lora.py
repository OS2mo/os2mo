# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import collections
import itertools
import re
import uuid
from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Container
from collections.abc import Coroutine
from collections.abc import ItemsView
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Sequence
from contextlib import contextmanager
from contextlib import suppress
from datetime import date
from datetime import datetime
from datetime import time
from enum import Enum
from enum import unique
from functools import partial
from itertools import starmap
from typing import Any
from typing import Literal
from typing import TypeVar
from typing import overload
from uuid import UUID

from fastapi import Request
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from oio_rest import custom_exceptions as loraexc
from oio_rest import klassifikation
from oio_rest import organisation
from oio_rest.db import _parse_timestamp
from oio_rest.mo.autocomplete import find_org_units_matching
from oio_rest.mo.autocomplete import find_users_matching
from sqlalchemy.exc import DataError
from starlette_context import context
from starlette_context import request_cycle_context
from strawberry.dataloader import DataLoader
from structlog import get_logger

from . import config
from . import exceptions
from . import util
from .db import get_session
from .graphapi.middleware import is_graphql

T = TypeVar("T")
V = TypeVar("V")
ValidityLiteral = Literal["past", "present", "future"]


logger = get_logger()


def filter_registrations(
    response: list[dict[str, Any]],
    wantregs: bool,
) -> Iterable[tuple[str, list[dict[str, Any]] | dict[str, Any]]]:
    """
    Helper, to filter registrations
    :param response: Registrations as received from LoRa
    :param wantregs: Determines whether one or more registrations are returned per uuid
    :return: Iterable of (uuid, registration(s))
    """

    # funny looking, but keeps api backwards compatible (ie avoiding 'async for')
    def gen():
        for d in response:
            regs = list(d["registreringer"])
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


_MIDDLEWARE_KEY = "lora_noop_change"


async def lora_noop_change_context(request: Request, call_next) -> Response:
    """
    Middleware to expose LoRa "no-op" changes to the frontend in an infuriatingly bad way.
    """
    data = {**context, _MIDDLEWARE_KEY: False}
    with request_cycle_context(data):
        response = await call_next(request)

        if context.get(_MIDDLEWARE_KEY):
            response.headers["X-DEPRECATED-LORA-NOOP-CHANGE-DO-NOT-USE"] = "1"
        return response


def get_msg_and_cause(e: loraexc.OIOException) -> dict[str, Any]:
    d = e.to_dict()
    return {"message": d.get("message", ""), "cause": d.get("context")}


@contextmanager
def lora_to_mo_exception() -> Iterator[None]:
    try:
        yield
    except loraexc.NotFoundException as e:
        exceptions.ErrorCodes.E_NOT_FOUND(**get_msg_and_cause(e))
    except loraexc.UnauthorizedException as e:
        exceptions.ErrorCodes.E_UNAUTHORIZED(**get_msg_and_cause(e))
    except loraexc.AuthorizationFailedException as e:
        exceptions.ErrorCodes.E_FORBIDDEN(**get_msg_and_cause(e))
    except (loraexc.BadRequestException, loraexc.DBException) as e:
        d = get_msg_and_cause(e)
        msg, cause = d["message"], d["cause"]

        noop_pattern = re.compile(
            r"Aborted updating \w+ with id \[.*\] as the given data, does not "
            r"give raise to a new registration"
        )
        # If LoRa returns HTTP status code 400, first check if the error
        # reported indicates a "no-op" change (no data was actually changed in
        # the update.)
        if noop_pattern.search(msg):
            logger.info(
                "detected empty change, not raising E_INVALID_INPUT", message=msg
            )
            # Set context var to expose this (otherwise masked) error through an HTTP
            # header.
            context[_MIDDLEWARE_KEY] = True
        else:
            exceptions.ErrorCodes.E_INVALID_INPUT(message=msg, cause=cause)
    except ValueError as e:
        exceptions.ErrorCodes.E_INVALID_INPUT(message=e.args[0], cause=None)
    except DataError as e:
        message = e.orig.diag.message_primary
        cause = e.orig.diag.context
        exceptions.ErrorCodes.E_INVALID_INPUT(message=message, cause=cause)
    except Exception as e:
        try:
            exceptions.ErrorCodes.E_UNKNOWN(message=e.args[0], cause=None)
        except IndexError:
            exceptions.ErrorCodes.E_UNKNOWN()


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
    params: dict[T, bool | list | set | str | int | uuid.UUID],
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
    validity: ValidityLiteral, now: date | datetime | None = None
) -> tuple[date | datetime, date | datetime]:
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
        )
        if config.get_settings().consolidate:
            # LoRa does not check the value of the 'konsolider' paramter, but the mere
            # existence of the _key_. For this reason, the value CANNOT be set to
            # False, it must instead be absent from the dict.
            defaults.update(
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
    def get_key_for_path(cls, path: Iterable[str | int]) -> str | int:
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

        _, class_str = path.split("/")

        match class_str:
            case "facet":
                self.lora_class = klassifikation.Facet
            case "klasse":
                self.lora_class = klassifikation.Klasse
            case "bruger":
                self.lora_class = organisation.Bruger
            case "itsystem":
                self.lora_class = organisation.ItSystem
            case "organisation":
                self.lora_class = organisation.Organisation
            case "organisationenhed":
                self.lora_class = organisation.OrganisationEnhed
            case "organisationfunktion":
                self.lora_class = organisation.OrganisationFunktion


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
            not config.get_settings().bulked_fetch
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
            uuids = {r["id"] for r in uuid_results}

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

    async def fetch(self, **params):
        # Yea, this is an ugly way to format the args. We do this as long as we
        # still need to expose the LoRa HTTP/json API.
        args = []
        for k, v in param_exotics_to_strings(
            {**self.connector.defaults, **params}
        ).items():
            if isinstance(v, Sequence) and not isinstance(v, str):
                for v2 in v:
                    args.append((k, v2))
            else:
                args.append((k, v))

        with lora_to_mo_exception():
            result = await self.lora_class.get_objects_direct(args)
        with suppress(IndexError):
            return jsonable_encoder(result["results"][0])

        # The requested GraphQL pagination is out of range if LoRa returned no results
        # _because_ of the provided pagination parameters. This check cannot easily be
        # done at a higher level because the MO reading handlers filter (potentially
        # all of) the results on top of the SQL filtering in LoRa.
        # We don't do anything special here, but set a contextvar which can be read by
        # the GraphQL middleware to return the error to the user.
        limit = params.get("maximalantalresultater")
        offset = params.get("foersteresultat", 0)
        is_paged = is_graphql() and limit != 0 and offset > 0
        if is_paged:
            # There may be multiple LoRa fetches in one GraphQL request, so this cannot
            # be refactored into always overwriting the value.
            context["lora_page_out_of_range"] = True

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

        response = await self.load(**params)
        wantregs = not params.keys().isdisjoint({"registreretfra", "registrerettil"})
        return filter_registrations(response=response, wantregs=wantregs)

    async def get_all_by_uuid(
        self,
        uuids: list | set,
    ) -> Iterable[tuple[str, dict[Any, Any]]]:
        """
        Get a list of objects by their UUIDs.
        Returns an iterator of tuples (obj_id, obj) of all matches.
        """
        ret = await self.load(uuid=uuids)
        return filter_registrations(response=ret, wantregs=False)

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
            obj_iter = [await func(self.connector, *tup) for tup in obj_iter]
        else:
            obj_iter = starmap(partial(func, self.connector), obj_iter)

        return {"total": total, "offset": start, "items": list(obj_iter)}

    @overload
    async def get(
        self, uuid: str | UUID, registreretfra: Any, **params: dict[str, Any]
    ) -> list[dict] | None: ...

    @overload
    async def get(
        self, uuid: str | UUID, registrerettil: Any, **params: dict[str, Any]
    ) -> list[dict] | None: ...

    @overload
    async def get(self, uuid: str | UUID, **params: dict[str, Any]) -> dict | None: ...

    async def get(
        self, uuid: str | UUID, **params: dict[str, Any]
    ) -> list[dict] | dict | None:
        """Fetch registration(s) for a single object from LoRa.

        Args:
            uuid: UUID to fetch registrations for in LoRa.
            params: Parameters to send along with the request.

        Returns:
            None if the object could not be found,
            None if the object has no registrations,
            A list of registrations if registreretfra or registrerettil is in params,
            A single registration otherwise.
        """
        d = await self.load(uuid=str(uuid), **params)
        # If object was not found => return None
        if not d:
            return None
        # We expect exactly one object as UUIDs are unique
        obj = one(d)
        # If the object does not have registrations => return None
        if not obj:
            return None
        # Extract registrations
        registrations = obj["registreringer"]
        # If our parameters included a registration time interval
        # We expect a list of registrations
        if params.keys() & {"registreretfra", "registrerettil"}:
            return registrations
        # If we did not include an interval, we expect only one registration
        return one(registrations)

    async def create(self, obj, uuid=None) -> str:
        obj = uuid_to_str(obj)

        with lora_to_mo_exception():
            if uuid:
                result = await self.lora_class.put_object_direct(uuid, obj, {})
            else:
                result = await self.lora_class.create_object_direct(obj, {})

        return str(result["uuid"])

    async def delete(self, uuid: uuid.UUID) -> uuid.UUID:
        with lora_to_mo_exception():
            result = await self.lora_class.delete_object_direct(uuid, {})
        return result.get("uuid", uuid)

    async def update(self, obj, uuid):
        result = {}
        with lora_to_mo_exception():
            try:
                result = await self.lora_class.patch_object_direct(uuid, obj)
            except loraexc.NotFoundException:
                logger.warning("could not update nonexistent LoRa object", uuid=uuid)
                return None
        return result.get("uuid", uuid)

    async def get_effects(self, obj, relevant, also=None, **params):
        reg = (
            await self.get(obj, **params) if isinstance(obj, (str, uuid.UUID)) else obj
        )

        if not reg:
            return

        effects = list(get_effects(reg, relevant, also))

        return filter(
            lambda a: self.connector.is_range_relevant(*a),  # noqa: FURB111
            effects,
        )


class AutocompleteScope(BaseScope):
    def __init__(self, connector, path):
        self.connector = connector
        if path == "bruger":
            self.autocomplete = find_users_matching
        elif path == "organisationsenhed":
            self.autocomplete = find_org_units_matching
        else:
            raise ValueError(f'{path} must be "bruger" or "organisationsenhed')

    async def fetch(
        self, phrase: str, class_uuids: list[UUID] | None = None
    ) -> dict[str, Any]:
        with lora_to_mo_exception():
            items = await self.autocomplete(
                get_session(), phrase, class_uuids=class_uuids
            )
            return {"items": items}


def get_effects(obj: dict, relevant: dict, additional: dict = None):
    """
    Splits a LoRa object up into several objects, based on changes in
    specified attributes

    The parameters 'relevant' and 'additional' detail which attributes to split
    on and which additional attributes to include in the objects, respectively.
    Both follow the same structure.

    A dict with the three 'groups' found in LoRa objects as keys, with the
    values being a tuple of the keys of the individual fields. E.g.:

    {
        "relationer": ('enhedstype', 'opgaver')
    }

    :param obj: A LoRa object
    :param relevant: The attributes to split on
    :param additional: Additional attributes to include in the result
    :return:
    """
    chunks = set()

    everything = collections.defaultdict(tuple)

    for group in relevant:
        everything[group] += relevant[group]
    for group in additional or {}:
        everything[group] += additional[group]

    # extract all beginning and end timestamps for all effects
    for group, keys in relevant.items():
        if group not in obj:
            continue

        entries = obj[group]

        for key in keys:
            if key not in entries:
                continue

            for entry in entries[key]:
                chunks.update(
                    (
                        _parse_timestamp(entry["virkning"]["from"]),
                        _parse_timestamp(entry["virkning"]["to"]),
                    )
                )

    # sort them, and apply the filter, if given
    chunks = itertools.pairwise(sorted(chunks))

    def filter_list(entries, start, end):
        for entry in entries:
            entry_start = _parse_timestamp(entry["virkning"]["from"])
            entry_end = _parse_timestamp(entry["virkning"]["to"])

            if entry_start < end and entry_end > start:
                yield entry

    # finally, extract chunks corresponding to each cut-off
    for start, end in chunks:
        effect = {
            group: {
                key: list(filter_list(obj[group][key], start, end))
                for key in everything[group]
                if key in everything[group] and key in obj[group]
            }
            for group in everything
            if group in obj
        }

        if any(k for g in effect.values() for k in g.values()):
            yield start, end, effect
