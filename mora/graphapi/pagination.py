# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pagination helpers.

This module provides a new pagination architecture where resolvers return
results wrapped in a Page object with calculated next_cursor, rather than
signaling out-of-range pagination through the lora_page_out_of_range context var.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

from sqlalchemy import SQLNOW

from mora.graphapi.filters import BaseFilter
from mora.graphapi.types import Cursor
from mora.graphapi.types import CursorType
from mora.util import now

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """Container for paginated results.

    Attributes:
        items: The list of result items.
        next_cursor: Cursor for the next page, or None if no more pages.
    """

    items: Sequence[T]
    next_cursor: CursorType


def paginate(
    results: Sequence[T],
    limit: int | None,
    cursor: CursorType,
    filter: Any | None = None,
    *,
    fetch_extra: bool = False,
) -> Page[T]:
    """Create a paginated result with calculated next_cursor.

    This function replaces the old pattern where resolvers would signal
    out-of-range pagination through the lora_page_out_of_range context var.
    Instead, each resolver returns results wrapped in a Page, calculating
    the next_cursor directly.

    Args:
        results: The list of result items from the resolver query.
        limit: The maximum number of items requested.
        cursor: The cursor defining the starting position.
        filter: Optional filter object (used for registration_time).
        fetch_extra: If True, assumes one extra item was fetched for
            pagination checking and strips it.

    Returns:
        A Page object with items and calculated next_cursor.
    """
    if not limit or cursor is None:
        return Page(items=results, next_cursor=None)

    registration_time = _get_registration_time(filter, cursor)

    if fetch_extra:
        has_more = len(results) > limit
        if has_more:
            results = results[:-1]
    else:
        has_more = len(results) == limit

    if not has_more:
        return Page(items=results, next_cursor=None)

    next_cursor = Cursor(
        last=UUID(int=int(cursor.last) + limit),
        registration_time=registration_time,
    )
    return Page(items=results, next_cursor=next_cursor)


def _get_registration_time(
    filter: Any | None,
    cursor: CursorType,
) -> datetime | SQLNOW:
    """Get the registration time for pagination cursor.

    Folded from the old resolvers._get_registration_time function.
    This is now internal to the pagination module.

    Args:
        filter: Filter object that may contain registration_time.
        cursor: Cursor containing registration_time.

    Returns:
        The registration time to use for the cursor.

    Raises:
        ValueError: If registration_time changes during pagination.
    """
    from mora.graphapi.types import Cursor as CursorModel

    if (
        cursor is not None
        and isinstance(filter, BaseFilter)
        and filter.registration_time
        and filter.registration_time != cursor.registration_time
    ):
        raise ValueError("Cannot change registration_time during pagination")

    if cursor is not None:
        return cursor.registration_time
    if isinstance(filter, BaseFilter) and filter.registration_time:
        return filter.registration_time
    return now()
