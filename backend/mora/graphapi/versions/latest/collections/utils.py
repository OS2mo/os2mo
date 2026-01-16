# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Utility functions for GraphQL schema."""

from collections.abc import Awaitable
from collections.abc import Callable
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

from strawberry import UNSET
from strawberry.types import Info

from ..graphql_utils import LoadKey
from ..moobject import MOObject
from ..paged import to_paged
from ..resolver_map import resolver_map
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
    mapper: Callable[[ResolverResult, Info], R],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[R]]]:
    def wrapper(
        resolver_func: ResolverFunction,
    ) -> Callable[..., Awaitable[R]]:
        @wraps(resolver_func)
        async def mapped_resolver(*args: Any, **kwargs: Any) -> Any:
            info = kwargs.get("info")
            if info is None:
                info = next(arg for arg in args if isinstance(arg, Info))
            result = await resolver_func(*args, **kwargs)
            return mapper(result, info)

        return mapped_resolver

    return wrapper


def to_response(
    model: type[MOObject],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[Response[MOObject]]]]:
    def result2response_list(
        result: ResolverResult,
        info: Info,
    ) -> Response[MOObject]:  # pragma: no cover
        uuid, objects = one(result.items())
        resolver = resolver_map[model]["loader"]
        dataloader = info.context[resolver]
        dataloader.prime(LoadKey(uuid, UNSET, UNSET, None), objects)
        return Response(model=model, uuid=uuid)

    return result_translation(result2response_list)


def to_response_list(
    model: type[MOObject],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[list[Response[MOObject]]]]]:
    def result2response_list(
        result: ResolverResult,
        info: Info,
    ) -> list[Response[MOObject]]:
        responses = []
        for uuid, objects in result.items():
            resolver = resolver_map[model]["loader"]
            dataloader = info.context[resolver]
            dataloader.prime(LoadKey(uuid, UNSET, UNSET, None), objects)
            responses.append(Response(model=model, uuid=uuid))
        return responses

    return result_translation(result2response_list)


to_list = result_translation(
    lambda result, _: list(chain.from_iterable(result.values())),
)
to_only = result_translation(
    lambda result, _: only(chain.from_iterable(result.values())),
)
to_one = result_translation(
    lambda result, _: one(chain.from_iterable(result.values())),
)
to_arbitrary_only = result_translation(
    lambda result, _: last(chain.from_iterable(result.values()), default=None),
)


def to_paged_response(model: type[MOObject]) -> Callable:
    def result_transformer(
        model: type[MOObject], result: ResolverResult, info: Info
    ) -> list[Response[MOObject]]:
        responses = []
        for uuid, objects in result.items():
            resolver = resolver_map[model]["loader"]
            dataloader = info.context[resolver]
            dataloader.prime(LoadKey(uuid, UNSET, UNSET, None), objects)
            responses.append(Response(model=model, uuid=uuid))
        return responses

    return partial(
        to_paged,
        model=model,
        result_transformer=result_transformer,
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
