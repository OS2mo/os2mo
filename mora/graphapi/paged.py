# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

import strawberry
from pydantic import PositiveInt
from sqlalchemy import Select
from sqlalchemy import func
from sqlalchemy.sql.functions import now as SQLNOW
from strawberry.types import Info

from mora.db import AsyncSession
from mora.util import now

from .filters import BaseFilter
from .gmodels.base import tz_isodate
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


@dataclass
class Page(Generic[T]):
    """A resolver's native result together with the cursor for the next page.

    Resolvers compute their own `next_cursor`, rather than signalling
    end-of-iteration out-of-band. `objects` is the resolver's native result type
    (a `dict[UUID, list[MOObject]]` for the entity resolvers, a `list` for the
    others); `to_paged` and `result_translation` unwrap it.
    """

    objects: T
    next_cursor: CursorType = None


def advance_cursor(cursor: Cursor, limit: int) -> Cursor:
    """The cursor for the next page: same registration snapshot, offset advanced."""
    return Cursor(
        last=UUID(int=int(cursor.last) + limit),
        registration_time=cursor.registration_time,
    )


def seed_cursor(cursor: CursorType, limit: LimitType) -> CursorType:
    """Seed the first-page cursor for list-based resolvers.

    Pins the registration snapshot for the whole iteration. Entity resolvers seed
    via `paginate_setup` instead, since they derive the snapshot time from the
    filter as well.
    """
    if limit and cursor is None:
        return Cursor(last=UUID(int=0), registration_time=now())
    return cursor


def next_page(cursor: CursorType, limit: LimitType, has_more: bool) -> CursorType:
    """Next-page cursor for list-based resolvers; cursor must already be seeded."""
    if limit and has_more:
        assert cursor is not None
        return advance_cursor(cursor, limit)
    return None


def paginate_setup(
    filter: BaseFilter,
    limit: LimitType,
    cursor: CursorType,
) -> tuple[CursorType, datetime | SQLNOW]:
    """Set up cursor-based pagination for the entity resolvers.

    Seeds the first-page cursor (pinning the registration snapshot from the filter
    or `now()`) and resolves the bitemporal registration time used by the
    predicate. Returns the (possibly seeded) cursor and the registration time.
    """
    # Reject changing the registration time mid-pagination. Compared against the
    # incoming cursor, before seeding.
    if (
        cursor is not None
        and filter.registration_time
        and filter.registration_time != cursor.registration_time
    ):
        raise ValueError("Cannot change registration_time during pagination")

    if limit and cursor is None:
        cursor = Cursor(
            last=UUID(int=0),
            registration_time=filter.registration_time or now(),
        )

    if cursor is not None:
        return cursor, tz_isodate(cursor.registration_time)
    if filter.registration_time:
        return cursor, tz_isodate(filter.registration_time)
    return cursor, func.now()


def offset_next_cursor(
    cursor: CursorType, limit: LimitType, results: Sequence[Any]
) -> CursorType:
    """Next-page cursor for offset-based pagination, or None when exhausted.

    An empty page beyond the first (cursor.last > 0) means iteration is done. An
    empty *first* page still yields a cursor: limiting is applied in the database
    layer before object consolidation, so a short page does not imply the end.
    """
    if not limit or cursor is None:
        return None
    if not results and int(cursor.last) > 0:
        return None
    return advance_cursor(cursor, limit)


async def paginate(
    session: AsyncSession,
    query: Select,
    limit: LimitType,
    cursor: CursorType,
) -> tuple[Sequence[UUID], CursorType]:
    """Apply offset/limit to `query`, execute it, and compute the next cursor.

    Used by the entity resolvers, which page by selecting a `distinct` UUID column.
    The next cursor is derived from the raw UUIDs returned by the database, not the
    consolidated objects, since further filtering may happen in MO afterwards.
    """
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(int(cursor.last))
    uuids = (await session.scalars(query)).all()
    return uuids, offset_next_cursor(cursor, limit, uuids)


def to_objects(
    resolver_func: Callable[..., Awaitable[Page]],
) -> Callable[..., Awaitable[Any]]:
    """Adapt a Page-returning resolver for a field exposing its raw object list.

    Used for (seeded) list-returning resolvers surfaced directly as a list field,
    without pagination metadata; the next cursor is discarded.
    """

    @wraps(resolver_func)
    async def unwrap(info: Info, *args: Any, **kwargs: Any) -> Any:
        page = await resolver_func(*args, info=info, **kwargs)
        return page.objects

    return unwrap


def to_paged(
    resolver_func: Callable[..., Awaitable[Page]],
    model: Any,
    result_transformer: Callable[[Any, Any, Info], Any] | None = None,
) -> Callable[..., Awaitable[Paged]]:
    result_transformer = result_transformer or (lambda _, x, __: x)

    @wraps(resolver_func)
    async def resolve_response(
        *args: Any,
        info: Info,
        limit: LimitType,
        cursor: CursorType,
        filter: Any = None,
        **kwargs: Any,
    ) -> Paged:
        page = await resolver_func(
            *args, info=info, filter=filter, limit=limit, cursor=cursor, **kwargs
        )
        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(model, page.objects, info),
            page_info=PageInfo(next_cursor=page.next_cursor),  # type: ignore[call-arg]
        )

    return resolve_response
