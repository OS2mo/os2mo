# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import wraps
from textwrap import dedent
from typing import Any
from typing import Generic
from typing import TypeVar

import strawberry
from starlette_context import context

from .resolvers import CursorType
from .resolvers import LimitType
from .resolvers import PagedResolver
from .types import Cursor
from mora.util import now


T = TypeVar("T")


@strawberry.type(
    description=dedent(
        """\
    Container for page information.

    Contains the cursors necessary to fetch other pages.
    Contains information on when to stop iteration.
    """
    )
)
class PageInfo:
    next_cursor: CursorType = strawberry.field(
        description=dedent(
            """\
            Cursor for the next page of results.

            Should be provided to the `cursor` argument to iterate forwards.
            """
        ),
        default=None,
    )


@strawberry.type(description="Result page in cursor-based pagination.")
class Paged(Generic[T]):
    objects: list[T] = strawberry.field(
        description=dedent(
            """\
            List of results.

            The number of elements is defined by the `limit` argument.
            """
        )
    )
    page_info: PageInfo = strawberry.field(
        description=dedent(
            """\
            Container for page information.

            Contains the cursors necessary to fetch other pages.
            Contains information on when to stop iteration.
            """
        )
    )


def to_paged(resolver: PagedResolver, result_transformer: Callable[[PagedResolver, Any], list[Any]] | None = None):  # type: ignore
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver.resolve)
    async def resolve_response(*args, limit: LimitType, cursor: CursorType, **kwargs):  # type: ignore
        if limit and cursor is None:
            cursor = Cursor(
                offset=0,
                registration_time=str(now()),
            )

        result = await resolver.resolve(*args, limit=limit, cursor=cursor, **kwargs)

        end_cursor: CursorType = None
        if limit and cursor is not None:
            end_cursor = Cursor(
                offset=cursor.offset + limit,
                registration_time=cursor.registration_time,
            )
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(resolver, result),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response
