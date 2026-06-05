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
from uuid import UUID

import strawberry
from pydantic import PositiveInt
from starlette_context import context
from strawberry.types import Info

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


def paginate_uuids(
    uuids: list[UUID],
    limit: int | None,
    cursor: CursorType,
    filter: BaseFilter | RegistrationFilter | None = None,
) -> tuple[list[UUID], CursorType]:
    """
    Apply cursor-based pagination to a list of UUIDs.

    Args:
        uuids: The full list of UUIDs to paginate
        limit: Maximum number of items per page
        cursor: Current pagination cursor
        filter: Optional filter containing registration time

    Returns:
        tuple: (paginated_uuids, next_cursor)
    """
    # Handle registration time logic
    if cursor is None:
        registration_time = now()
        if isinstance(filter, BaseFilter) and filter.registration_time:
            registration_time = filter.registration_time
        cursor = Cursor(last=UUID(int=0), registration_time=registration_time)

    # Calculate page boundaries
    start_idx = int(cursor.last.int)
    end_idx = start_idx + (limit or len(uuids))

    # Get page UUIDs
    page_uuids = uuids[start_idx:end_idx]

    # Calculate next cursor
    next_cursor = None
    if limit and end_idx < len(uuids):
        next_cursor = Cursor(
            last=UUID(int=end_idx),
            registration_time=cursor.registration_time,
        )

    return page_uuids, next_cursor


def paginate(
    items: list[T],
    limit: int | None,
    cursor: CursorType,
    filter: BaseFilter | RegistrationFilter | None = None,
) -> Paged[T]:
    """
    Apply cursor-based pagination to a list of items.

    Args:
        items: The full list of items to paginate
        limit: Maximum number of items per page
        cursor: Current pagination cursor
        filter: Optional filter containing registration time

    Returns:
        Paged: A paginated response containing the page of items
    """
    # Use the UUID pagination logic and adapt for items
    if not items:
        return Paged(objects=[], page_info=PageInfo(next_cursor=None))

    # Handle registration time logic
    if cursor is None:
        registration_time = now()
        if isinstance(filter, BaseFilter) and filter.registration_time:
            registration_time = filter.registration_time
        cursor = Cursor(last=UUID(int=0), registration_time=registration_time)

    # Calculate page boundaries
    start_idx = int(cursor.last.int)
    end_idx = start_idx + (limit or len(items))

    # Get page items
    page_items = items[start_idx:end_idx]

    # Calculate next cursor
    next_cursor = None
    if limit and end_idx < len(items):
        next_cursor = Cursor(
            last=UUID(int=end_idx),
            registration_time=cursor.registration_time,
        )

    return Paged(
        objects=page_items,
        page_info=PageInfo(next_cursor=next_cursor)
    )


def to_paged(
    resolver_func: Callable[..., Awaitable[Any]],
    model: Any,
    result_transformer: Callable[[Any, Any, Info], Any] | None = None,
) -> Callable[..., Awaitable[Paged]]:
    """
    Deprecated: Use the paginate() helper directly.
    """
    warnings.warn(
        "to_paged is deprecated and will be removed in a future version. "
        "Use the paginate() helper directly.",
        DeprecationWarning,
        stacklevel=2,
    )
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
        result = await resolver_func(
            *args, info=info, filter=filter, limit=limit, cursor=cursor, **kwargs
        )

        # Use the new paginate helper
        transformed_items = result_transformer(model, result, info)
        return paginate(
            items=transformed_items,
            limit=limit,
            cursor=cursor,
            filter=filter,
        )

    return resolve_response
