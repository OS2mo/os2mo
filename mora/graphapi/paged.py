# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from collections.abc import Awaitable
from collections.abc import Callable
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
from sqlalchemy import func
from sqlalchemy.sql.functions import now as SQLNOW

from mora.graphapi.gmodels.base import tz_isodate
from mora.util import now

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
class Pagination:
    """Cursor-based pagination state for a single resolver call.

    Constructed once per call via `from_args`, which derives the query `offset` and the
    bitemporal `registration_time` snapshot from the incoming `filter`/`cursor`/`limit`.
    Resolvers run their query, decide locally whether another page exists, and call
    `page` to wrap the results and compute the `next_cursor`.
    """

    limit: int | None
    offset: int
    registration_time: datetime | SQLNOW

    @classmethod
    def from_args(
        cls,
        filter: Any,
        cursor: CursorType,
        limit: LimitType,
    ) -> "Pagination":
        offset = int(cursor.last) if cursor is not None else 0
        return cls(
            limit=limit,
            offset=offset,
            registration_time=cls._registration_time(filter, cursor, limit),
        )

    @staticmethod
    def _registration_time(
        filter: Any,
        cursor: CursorType,
        limit: LimitType,
    ) -> datetime | SQLNOW:
        # `getattr`: RegistrationFilter and AccessLogFilter have no `registration_time`.
        filter_time = getattr(filter, "registration_time", None)
        if cursor is not None:
            if filter_time and filter_time != cursor.registration_time:
                raise ValueError("Cannot change registration_time during pagination")
            return tz_isodate(cursor.registration_time)
        if filter_time:
            return tz_isodate(filter_time)
        # The first page of a paginated query freezes a concrete time, so the snapshot
        # stays stable across pages and can be carried in the next_cursor.
        if limit:
            return now()
        return func.now()

    def page(self, objects: Any, *, has_next_page: bool) -> Paged:
        """Wrap resolved objects in a `Paged`, computing the next cursor.

        `has_next_page` is decided by the resolver, since the different resolver families
        detect the end of iteration differently (empty page, `limit + 1` lookahead, etc).
        """
        next_cursor: CursorType = None
        if self.limit and has_next_page:
            next_cursor = Cursor(
                last=UUID(int=self.offset + self.limit),
                registration_time=self.registration_time,
            )
        return Paged(  # type: ignore[call-arg]
            objects=objects,
            page_info=PageInfo(next_cursor=next_cursor),  # type: ignore[call-arg]
        )


def unpaged(
    resolver_func: Callable[..., Awaitable[Paged]],
) -> Callable[..., Awaitable[list[Any]]]:
    """Adapt a paginated resolver for a plain `list` field by dropping the page info.

    Some fields expose a resolver that returns a `Paged`, but the field itself is a bare
    `list` (e.g. the nested `registrations` field on responses). This unwraps the objects.
    """

    @wraps(resolver_func)
    async def resolve(*args: Any, **kwargs: Any) -> list[Any]:
        page = await resolver_func(*args, **kwargs)
        return page.objects

    return resolve
