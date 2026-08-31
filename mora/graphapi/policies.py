# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The policies: a collection's types, and which of its objects may be seen.

Access is collection-based, not route-based: it does not matter how a
collection is reached, only which of its objects the caller may read. A
collection is anchored to the GraphQL types its objects are exposed through,
and every read starts from the collection's predicate, which selects the
objects the caller may see. Lacking the role yields an empty collection
rather than a denial: the caller may always ask, and simply sees nothing.

Only the address collection is expressed here so far; the rest of the access
still lives in the path-based `RBAC_MAP` and `PUBLIC_FIELDS` of
`mora.graphapi.rbac_map`.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ColumnElement
from sqlalchemy import false
from sqlalchemy import true

from mora.graphapi.permissions import Collections

if TYPE_CHECKING:
    from mora.graphapi.context import MOContext

# The GraphQL types each collection's objects are read through: the objects
# themselves, and the bitemporal containers wrapping them.
COLLECTION_TYPES: dict[Collections, frozenset[str]] = {
    "address": frozenset({"Address", "AddressResponse", "AddressResponsePaged"}),
}

# Every type belonging to some collection
COLLECTION_TYPE_NAMES: frozenset[str] = frozenset(
    name for names in COLLECTION_TYPES.values() for name in names
)


async def address_read_predicate(context: "MOContext") -> ColumnElement[bool]:
    """The addresses readable by the caller: all of them, to the reader."""
    token = await context.get_token()
    if "reader" in token.realm_access.roles:
        return true()
    return false()
