# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime as _datetime
from functools import wraps
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

import strawberry
from pydantic import PositiveInt
from sqlalchemy import func as _sql_func
from starlette_context import context
from strawberry.types import Info

from mora.util import now

from .filters import BaseFilter
from .filters import RegistrationFilter
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


class PageHelper:
    """Pagination helper that computes registration_time, offset, and next_cursor.

    Replaces `_get_registration_time` and the cursor-manipulation logic
    previously done by `to_paged`.  Each paginated resolver creates an
    instance, uses `.registration_time` and `.offset` to build its query,
    and calls `.paged()` to wrap its result list.
    """

    def __init__(
        self,
        filter: BaseFilter | RegistrationFilter | None,
        cursor: CursorType,
        limit: LimitType,
    ) -> None:
        if (
            cursor is not None
            and isinstance(filter, BaseFilter)
            and filter.registration_time
            and filter.registration_time != cursor.registration_time
        ):
            raise ValueError("Cannot change registration_time during pagination")

        if cursor is not None:
            self._registration_time: _datetime | None = cursor.registration_time
            self._offset: int = int(cursor.last)
        elif isinstance(filter, BaseFilter) and filter.registration_time:
            self._registration_time = filter.registration_time
            self._offset = 0
        else:
            self._registration_time = None
            self._offset = 0

        self._limit: int | None = limit

    @property
    def registration_time(self) -> _datetime | Any:
        """Registration time for SQL predicates.

        Returns a timezone-aware datetime when a specific time is known,
        otherwise a SQL ``func.now()`` expression.
        """
        if self._registration_time is not None:
            return tz_isodate(self._registration_time)
        return _sql_func.now()

    @property
    def offset(self) -> int:
        """Row offset for SQL ``OFFSET`` clauses."""
        return self._offset

    def cursor(self, *, has_more: bool = True) -> CursorType:
        """Compute the cursor for the **next** page.

        Returns ``None`` when there are no more pages *or* when the
        original request did not include a ``limit``.
        """
        if not has_more or self._limit is None:
            return None
        reg_time = self._registration_time or now()
        return Cursor(
            last=UUID(int=self._offset + self._limit),
            registration_time=reg_time,
        )

    def paged(self, objects: list[T], *, has_more: bool = True) -> Paged[T]:
        """Wrap *objects* in a :class:`Paged` result."""
        return Paged(  # type: ignore[call-arg]
            objects=objects,
            page_info=PageInfo(next_cursor=self.cursor(has_more=has_more)),
        )


def to_paged(
    resolver_func: Callable[..., Awaitable[Any]],
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
        filter: BaseFilter | RegistrationFilter | None = None,
        **kwargs: Any,
    ) -> Paged:
        if limit and cursor is None:
            registration_time = now()
            # RegistrationFilter doesn't have a `registration_time`
            if isinstance(filter, BaseFilter) and filter.registration_time:
                registration_time = filter.registration_time
            cursor = Cursor(last=UUID(int=0), registration_time=registration_time)

        result = await resolver_func(
            *args, info=info, filter=filter, limit=limit, cursor=cursor, **kwargs
        )

        end_cursor: CursorType = None
        if limit and cursor is not None:
            end_cursor = Cursor(
                last=UUID(int=int(cursor.last) + limit),
                registration_time=cursor.registration_time,
            )
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(model, result, info),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response
