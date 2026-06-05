# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

import strawberry
from pydantic import PositiveInt

from mora.util import now

from .filters import BaseFilter
from .filters import RegistrationFilter
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


class Pagination(Generic[T]):
    def __init__(
        self,
        limit: LimitType,
        cursor: CursorType,
        filter: BaseFilter | RegistrationFilter | None = None,
    ):
        self.limit = limit
        self.filter = filter

        if limit and cursor is None:
            registration_time = now()
            if hasattr(filter, "registration_time") and filter.registration_time:
                registration_time = filter.registration_time
            self.cursor = Cursor(last=UUID(int=0), registration_time=registration_time)
        else:
            self.cursor = cursor

    @property
    def registration_time(self) -> Any:
        from sqlalchemy.sql import func

        from mora.graphapi.gmodels.base import tz_isodate

        if (
            self.cursor is not None
            and hasattr(self.filter, "registration_time")
            and getattr(self.filter, "registration_time", None)
            and getattr(self.filter, "registration_time", None)
            != self.cursor.registration_time
        ):
            raise ValueError("Cannot change registration_time during pagination")

        if self.cursor is not None:
            return tz_isodate(self.cursor.registration_time)
        if hasattr(self.filter, "registration_time") and getattr(
            self.filter, "registration_time", None
        ):
            return tz_isodate(getattr(self.filter, "registration_time"))
        return func.now()

    def apply(self, query: Any) -> Any:
        if self.limit is not None:
            query = query.limit(self.limit)
        if self.cursor is not None:
            query = query.offset(int(self.cursor.last))
        return query

    def apply_list(self, obj: list[Any]) -> list[Any]:
        if self.limit is None:
            return obj
        if self.cursor is None:
            return obj[: self.limit]
        return obj[int(self.cursor.last) :][: self.limit]  # pragma: no cover

    def create_page(self, objects: Any) -> Paged[T]:
        end_cursor: CursorType = None
        if self.limit and self.cursor is not None:
            if len(objects) == self.limit:
                end_cursor = Cursor(
                    last=UUID(int=int(self.cursor.last) + self.limit),
                    registration_time=self.cursor.registration_time,
                )
        return Paged(
            objects=objects,
            page_info=PageInfo(next_cursor=end_cursor),
        )
