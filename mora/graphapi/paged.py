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


# Above this many matching rows, a result is dense enough that an ordered
# index scan is guaranteed to fill its page LIMIT early.
PROBE_CAP = 10_000


async def paginate(
    session: AsyncSession,
    query: Select,
    column: SQLColumnExpression[UUID],
    limit: LimitType,
    cursor: CursorType,
) -> tuple[Sequence[UUID], CursorType]:
    """Paginate `query`, which must be unordered and without DISTINCT.

    Combining `ORDER BY column` with a small LIMIT baits the planner into an
    abort-early plan: walk the ordering index, filter each row, and hope to
    fill the LIMIT early. Its cost model assumes matching rows are uniformly
    distributed, so when they are clumped -- e.g. an org unit whose
    engagements are all in the past -- the walk visits the entire table.

    To avoid this, first probe the filter without ORDER BY and without the
    page LIMIT, leaving the planner free to drive the query from whichever
    side is actually selective. The probe's cap bounds what we fetch and
    reveals which regime we are in: if the full remaining result fits under
    the cap, paginate it in Python; otherwise the result is dense and the
    ordered keyset query is safe.
    """
    if cursor is not None:
        query = query.where(column > cursor.last)

    if limit is None:
        # Without a LIMIT the planner costs the full result and never gambles
        # on early exit, so the ordered query is safe.
        uuids = (await session.scalars(query.distinct().order_by(column))).all()
        return uuids, None

    if limit == 0:
        # SQL LIMIT 0 semantics: an empty page with no next cursor.
        return [], None

    cap = max(PROBE_CAP, limit)
    # DISTINCT is applied in Python: in SQL it would force the database to
    # aggregate all matching rows before the cap could stop anything.
    rows = (await session.scalars(query.limit(cap + 1))).all()
    if len(rows) <= cap:
        # The complete remaining result is in hand. Python UUID comparison
        # matches Postgres uuid btree order, so cursors remain consistent
        # with the ordered query below.
        remaining = sorted(set(rows))
        page: Sequence[UUID] = remaining[:limit]
        if len(remaining) > len(page):
            return page, Cursor(last=page[-1])
        return page, None

    # Fetch one extra row to see if there is another page
    ordered = query.distinct().order_by(column).limit(limit + 1)
    uuids = (await session.scalars(ordered)).all()
    # `uuids[:limit]` drops the probe row; a longer `uuids` than the page
    # itself means another page exists.
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
