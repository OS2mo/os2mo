# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination primitives."""

from collections.abc import Awaitable
from collections.abc import Callable
from functools import wraps
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import TypeVar

import strawberry
from pydantic import PositiveInt
from starlette_context import context

from mora.util import now

from .filters import BaseFilter
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


def to_paged(  # type: ignore
    resolver_func: Callable,
    model: Any,
    result_transformer: Callable | None = None,
) -> Callable[..., Awaitable[Paged]]:
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver_func)
    async def resolve_response(
        *args: Any,
        limit: LimitType,
        cursor: CursorType,
        filter: BaseFilter | None = None,
        **kwargs: Any,
    ) -> Paged:
        if limit and cursor is None:
            registration_time = now()
            if filter is not None and filter.registration_time:
                registration_time = filter.registration_time
            cursor = Cursor(offset=0, registration_time=registration_time)

        result = await resolver_func(
            *args, filter=filter, limit=limit, cursor=cursor, **kwargs
        )

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
            objects=result_transformer(model, result),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response
