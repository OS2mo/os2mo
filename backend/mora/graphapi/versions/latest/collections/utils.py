# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Utility functions for GraphQL schema."""

from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime
from datetime import time
from functools import partial
from functools import wraps
from itertools import chain
from textwrap import dedent
from typing import Any
from typing import TypeVar
from uuid import UUID

from more_itertools import last
from more_itertools import one
from more_itertools import only
from pydantic import parse_obj_as

from mora.common import _create_graphql_connector
from mora.graphapi.gmodels.mo import OpenValidity as RAMOpenValidity
from mora.graphapi.middleware import with_graphql_dates
from mora.graphapi.versions.latest.readers import _extract_search_params
from mora.handler.reading import ReadingHandler

from ..moobject import MOObject
from ..paged import to_paged
from ..response import Response
from ..utils import uuid2list

R = TypeVar("R")


def raise_force_none_return_if_uuid_none(
    root: Any, get_uuid: Callable[[Any], UUID | None]
) -> list[UUID]:
    """Raise ForceNoneReturnError if uuid is None, a list with the uuid otherwise.

    Args:
        root: The root object from which the UUID will be extracted.
        get_uuid: Extractor function used to extract a UUID from root.

    Raises:
        ForceNonReturnError: If the extracted uuid is None.

    Returns:
        A list containing the UUID if the extracted uuid is not None.
    """
    uuid = get_uuid(root)
    if uuid is None:
        raise ForceNoneReturnError
    return uuid2list(uuid)


class ForceNoneReturnError(Exception):
    """Error to be raised to forcefully return None from decorated function.

    Note: The function that should forcefully return None must be decorated with
          `force_none_return_wrapper`.
    """

    pass


def force_none_return_wrapper(func: Callable) -> Callable:
    """Decorate a function to react to ForceNonReturnError.

    Args:
        func: The function to be decorated.

    Returns:
        A decorated function that returns None whenever ForceNonReturnError is raised.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R | None:
        try:
            return await func(*args, **kwargs)
        except ForceNoneReturnError:
            return None

    return wrapper


ResolverResult = dict[UUID, list[MOObject]]
ResolverFunction = Callable[..., Awaitable[ResolverResult]]


def result_translation(
    mapper: Callable[[ResolverResult], R],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[R]]]:
    def wrapper(
        resolver_func: ResolverFunction,
    ) -> Callable[..., Awaitable[R]]:
        @wraps(resolver_func)
        async def mapped_resolver(*args: Any, **kwargs: Any) -> Any:
            result = await resolver_func(*args, **kwargs)
            return mapper(result)

        return mapped_resolver

    return wrapper


def to_response(
    model: type[MOObject],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[Response[MOObject]]]]:
    def result2response_list(
        result: ResolverResult,
    ) -> Response[MOObject]:  # pragma: no cover
        uuid, objects = one(result.items())
        return Response(model=model, uuid=uuid, object_cache=objects)

    return result_translation(result2response_list)


def to_response_list(
    model: type[MOObject],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[list[Response[MOObject]]]]]:
    def result2response_list(result: ResolverResult) -> list[Response[MOObject]]:
        return [
            Response(model=model, uuid=uuid, object_cache=objects)
            for uuid, objects in result.items()
        ]

    return result_translation(result2response_list)


to_list = result_translation(
    lambda result: list(chain.from_iterable(result.values())),
)
to_only = result_translation(
    lambda result: only(chain.from_iterable(result.values())),
)
to_one = result_translation(
    lambda result: one(chain.from_iterable(result.values())),
)
to_arbitrary_only = result_translation(
    lambda result: last(chain.from_iterable(result.values()), default=None),
)


def to_paged_response(model: type[MOObject]) -> Callable:
    return partial(
        to_paged,
        model=model,
        result_transformer=lambda model, result: [
            Response(model=model, uuid=uuid, object_cache=objects)
            for uuid, objects in result.items()
        ],
    )


def gen_uuid_field_deprecation(field: str) -> str:
    """Generate a deprecation warning for `_uuid` fields.

    Args:
        field: Name of the field that has the `_uuid` ending.

    Returns:
        Deprecation message explaining how to fetch the field in the future.
    """
    return dedent(
        f"""
        Will be removed in a future version of GraphQL.
        Use `{field} {{uuid}}` instead.
        """
    )


# TODO: Remove list and make optional instead all the places this is used
list_to_optional_field_warning = dedent(
    """

    **Warning**:
    This field will probably become an optional entity instead of a list in the future.
    """
)


async def validity_sub_query_hack(
    root_validity: RAMOpenValidity,
    item_type: type[Any],
    item_reading_handler: ReadingHandler,
    item_lora_query_args: dict,
) -> list[Any]:
    # Custom Lora-GraphQL connector - created in order to control dates in sub-queries/recursions
    if root_validity.to_date:  # pragma: no cover
        # FYI: This is needed when ex root.validity.to_date == item.validity.from_date
        # If we just use "root_validity.to_date" where ex time is "00:00:00",
        # LoRa will return no results, since it needs the time to be "23:59:59" to be inclusive.
        root_validity = RAMOpenValidity(
            from_date=root_validity.from_date,
            to_date=datetime.combine(root_validity.to_date.date(), time.max),
        )

    with with_graphql_dates(root_validity):
        c = _create_graphql_connector()

    # potential items
    item_potentials = await item_reading_handler.get(
        c=c,
        search_fields=_extract_search_params(query_args=item_lora_query_args),
    )
    item_potentials_models = parse_obj_as(list[item_type], item_potentials)  # type: ignore

    # Filter out items where to_date is before root_validity.from_date
    item_potentials_models = list(
        filter(
            lambda ipm: (  # type: ignore
                root_validity.from_date is None  # type: ignore
                or ipm.validity.to_date is None  # type: ignore
                or ipm.validity.to_date  # type: ignore
                >= root_validity.from_date  # type: ignore
            ),
            item_potentials_models,
        )
    )

    # Filter out items where from_date is after root_validity.to_date
    item_potentials_models = list(
        filter(
            lambda ipm: (  # type: ignore
                root_validity.to_date is None  # type: ignore
                or ipm.validity.from_date is None  # type: ignore
                or ipm.validity.from_date  # type: ignore
                <= root_validity.to_date  # type: ignore
            ),
            item_potentials_models,
        )
    )

    # Go through models versions and if there are multiple with the same UUID,
    # use the one with the earliest from_date
    items_final: list[item_type] = []  # type: ignore
    for item in item_potentials_models:
        existing_item = next(
            (i for i in items_final if i.uuid == item.uuid),  # type: ignore
            None,
        )
        if existing_item is None:
            items_final.append(item)
        else:  # pragma: no cover
            # Handle the case where either from_date could be None
            if existing_item.validity.from_date is None or (
                item.validity.from_date is not None
                and item.validity.from_date  # type: ignore
                < existing_item.validity.from_date  # type: ignore
            ):
                items_final.remove(existing_item)
                items_final.append(item)

    return items_final
