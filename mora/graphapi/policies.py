# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Read policies: which fields of which objects a caller may read.

A rule, (collection, condition, fields), grants reading the fields of the
objects of a collection matching the condition, and a role's policy is its
rules. The caller may read a field of an object if a rule of one of their
roles grants it on that object, wherever the object is reached. Only the
fields of the address types are guarded this way so far; everything else is
still gated route by route in `mora.graphapi.rbac_map`.

The decisions are made through a dataloader, the access loader, answering
whether the caller may read a field of an object, so that all of a resolution
wave's, across collections, objects and fields alike, cost one lookup.
"""

from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

from more_itertools import flatten
from sqlalchemy import ARRAY
from sqlalchemy import ColumnElement
from sqlalchemy import Row
from sqlalchemy import Select
from sqlalchemy import String
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy import union_all
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import OrganisationFunktionRegistrering
from mora.graphapi.filters import AddressFilter
from mora.graphapi.resolvers import address_predicate

# A collection of objects guarded by policy, by the name of their GraphQL type
Collection: TypeAlias = str
# The fields of an object, by name
Fields: TypeAlias = frozenset[str]


def address_objects(uuids: set[UUID]) -> Select[tuple[UUID]]:
    """Select the addresses among *uuids*, as they stand now."""
    return select(
        distinct(OrganisationFunktionRegistrering.organisationfunktion_id)
    ).where(address_predicate(None, AddressFilter(uuids=list(uuids))))


# Each collection's select of its objects among some uuids, which alone knows
# its tables; a rule's condition narrows it to the objects it matches
OBJECTS_OF_COLLECTION: dict[Collection, Callable[[set[UUID]], Select[tuple[UUID]]]] = {
    "Address": address_objects,
}

# A rule, (collection, condition, fields): grants reading the fields of the
# objects of the collection matching the condition
Rule = tuple[Collection, ColumnElement[bool], Fields]

# The rules of each role. A caller's are those of their roles.
ROLE_POLICIES: dict[str, list[Rule]] = {
    "reader": [
        (
            "Address",
            true(),
            frozenset(
                {
                    "address_type",
                    "address_type_response",
                    "address_type_uuid",
                    "employee",
                    "employee_uuid",
                    "engagement",
                    "engagement_response",
                    "engagement_uuid",
                    "href",
                    "ituser",
                    "ituser_response",
                    "ituser_uuid",
                    "name",
                    "org_unit",
                    "org_unit_response",
                    "org_unit_uuid",
                    "person",
                    "person_response",
                    "resolve",
                    "type",
                    "user_key",
                    "uuid",
                    "validity",
                    "value",
                    "value2",
                    "visibility",
                    "visibility_response",
                    "visibility_uuid",
                }
            ),
        )
    ],
}


class AccessKey(NamedTuple):
    """An access: reading a field of an object of a collection."""

    collection: Collection
    uuid: UUID
    field: str


def uuids_by_collection(keys: Iterable[AccessKey]) -> dict[Collection, set[UUID]]:
    """Group the objects asked about by their collection."""
    grouped: dict[Collection, set[UUID]] = defaultdict(set)
    for collection, uuid, _ in keys:
        grouped[collection].add(uuid)
    return grouped


def rules_of(roles: Iterable[str]) -> list[Rule]:
    """The rules of the policies of *roles*."""
    return list(flatten(ROLE_POLICIES.get(role, []) for role in roles))


def rules_by_collection(
    rules: Iterable[Rule],
) -> dict[Collection, list[tuple[ColumnElement[bool], Fields]]]:
    """Group *rules* by their collection, as (condition, fields)."""
    grouped: dict[Collection, list[tuple[ColumnElement[bool], Fields]]] = defaultdict(
        list
    )
    for collection, condition, fields in rules:
        grouped[collection].append((condition, fields))
    return grouped


# A match, (collection, fields, objects): the objects a rule of the collection
# matched, which it grants the fields of
Match = tuple[Collection, Fields, Sequence[UUID]]


def matches_of(rows: Iterable[Row[Any]]) -> list[Match]:
    """The matches in the *rows* of the policy query, one per rule.

    Aggregating no objects gives null rather than an empty array.
    """
    return [
        (collection, Fields(fields), matching or [])
        for collection, fields, matching in rows
    ]


def fields_by_object(matches: Iterable[Match]) -> dict[Collection, dict[UUID, Fields]]:
    """The fields granted of each object in *matches*, by collection.

    Those of every rule matching it; none of an object no rule matched.
    """
    granted: dict[Collection, dict[UUID, Fields]] = defaultdict(
        lambda: defaultdict(Fields)
    )
    for collection, fields, objects in matches:
        for uuid in objects:
            granted[collection][uuid] |= fields
    return granted


async def access_load_fn(
    session: AsyncSession,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[AccessKey],
) -> list[bool]:
    """Whether the caller may read some fields of some objects, in one query.

    A union of one select per rule of the caller's roles for a collection in
    the batch, each returning the fields it grants and the objects matching
    its condition. An object gets the fields of every rule matching it.
    """
    roles = sorted((await get_token()).realm_access.roles)
    rules = rules_by_collection(rules_of(roles))
    selects: list[Select[Any]] = []
    for collection, uuids in uuids_by_collection(keys).items():
        objects = OBJECTS_OF_COLLECTION[collection]
        for condition, fields in rules.get(collection, []):
            matching = objects(uuids).where(condition).subquery()
            selects.append(
                select(
                    literal(collection),
                    literal(sorted(fields), ARRAY(String)),
                    func.array_agg(matching.c[0]),
                )
            )
    if not selects:
        # No rule applies, so the caller may read nothing of these objects
        return [False] * len(keys)
    rows = await session.execute(union_all(*selects))
    granted = fields_by_object(matches_of(rows))
    return [field in granted[collection][uuid] for collection, uuid, field in keys]


def get_access_loaders(
    session: AsyncSession, get_token: Callable[[], Awaitable[Token]]
) -> dict[str, DataLoader]:
    """Return the dataloader deciding what the caller may read."""
    return {
        "access_loader": DataLoader(
            load_fn=partial(access_load_fn, session, get_token)
        ),
    }
