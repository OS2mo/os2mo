# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Sequence
from functools import wraps
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import NamedTuple
from typing import TypeVar
from uuid import UUID

import strawberry
from pydantic import PositiveInt
from sqlalchemy import Select
from sqlalchemy import SQLColumnExpression
from strawberry.types import Info

from mora.db import AsyncSession

from .types import Cursor

LimitType = Annotated[
    PositiveInt | None,
    strawberry.argument(
        description=dedent(
            r"""
    Limit the maximum number of elements to fetch.

    | `limit`      | \# elements fetched |
    |--------------|---------------------|
    | not provided | All                 |
    | `null`       | All                 |
    | `0`          | `0` (`*`)           |
    | `x`          | Between `0` and `x` |

    `*`: This behavior is equivalent to SQL's `LIMIT 0` behavior.

    Note:

    Sometimes the caller may receieve a shorter list (or even an empty list) of results compared to the expected per the limit argument.

    This may seem confusing, but it is the expected behavior given the way that limiting is implemented in the bitemporal database layer, combined with how filtering and object change consolidation is handled.

    Not to worry; all the expected elements will eventually be returned, as long as the iteration is continued until the `next_cursor` is `null`.
    """
        )
    ),
]

CursorType = Annotated[
    Cursor | None,
    strawberry.argument(
        description=dedent(
            """\
    Cursor defining the next elements to fetch.

    | `cursor`       | Next element is    |
    |----------------|--------------------|
    | not provided   | First              |
    | `null`         | First              |
    | `"MA=="` (`*`) | First after Cursor |

    `*`: Placeholder for the cursor returned by the previous iteration.
    """
        )
    ),
]


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


class ObjectsAndCursor(NamedTuple, Generic[T]):
    objects: T
    next_cursor: CursorType = None


async def paginate(
    session: AsyncSession,
    query: Select,
    column: SQLColumnExpression[UUID],
    limit: LimitType,
    cursor: CursorType,
) -> tuple[Sequence[UUID], CursorType]:
    if cursor is not None:
        query = query.where(column > cursor.last)
    if limit is not None:
        # Fetch one extra row to see if there is another page
        query = query.limit(limit + 1)
    uuids = (await session.scalars(query)).all()
    # `uuids[:limit]` drops the probe row (and is a no-op when limit is None); a
    # longer `uuids` than the page itself means another page exists.
    page = uuids[:limit]
    if page and len(uuids) > len(page):
        return page, Cursor(last=page[-1])
    return page, None


def to_objects(
    resolver_func: Callable[..., Awaitable[ObjectsAndCursor]],
) -> Callable[..., Awaitable[Any]]:
    @wraps(resolver_func)
    async def resolve_response(*args: Any, **kwargs: Any) -> Any:
        page = await resolver_func(*args, **kwargs)
        return page.objects

    return resolve_response


def to_paged(
    resolver_func: Callable[..., Awaitable[ObjectsAndCursor]],
    result_transformer: Callable[[Any, Info], Any] = lambda objects, _: objects,
) -> Callable[..., Awaitable[Paged]]:
    @wraps(resolver_func)
    async def resolve_response(*args: Any, info: Info, **kwargs: Any) -> Paged:
        page = await resolver_func(*args, info=info, **kwargs)
        return Paged(
            objects=result_transformer(page.objects, info),
            page_info=PageInfo(next_cursor=page.next_cursor),
        )

    return resolve_response
