# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Various helper methods for GraphQL."""

from uuid import UUID


def uuid2list(uuid: UUID | None) -> list[UUID]:
    """Convert an optional uuid to a list.

    Args:
        uuid: Optional uuid to wrap in a list.

    Return:
        Empty list if uuid was none, single element list containing the uuid otherwise.
    """
    if uuid is None:
        return []
    return [uuid]
