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
wave's, across collections, objects and fields alike, cost one lookup, which
returns only the accesses to deny.
"""

from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

from more_itertools import flatten
from sqlalchemy import ARRAY
from sqlalchemy import ColumnElement
from sqlalchemy import Select
from sqlalchemy import Uuid
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


def uuids_by_access(
    keys: Iterable[AccessKey],
) -> dict[tuple[Collection, str], set[UUID]]:
    """Group the objects asked about by the collection and field asked for."""
    grouped: dict[tuple[Collection, str], set[UUID]] = defaultdict(set)
    for collection, uuid, field in keys:
        grouped[collection, field].add(uuid)
    return grouped


def rules_of(roles: Iterable[str]) -> list[Rule]:
    """The rules of the policies of *roles*."""
    return list(flatten(ROLE_POLICIES.get(role, []) for role in roles))


def denied_select(
    collection: Collection, field: str, uuids: set[UUID], rules: Iterable[Rule]
) -> Select[Any]:
    """Select the accesses to deny among reading *field* of *uuids*.

    Those of the objects matched by no rule granting the field.
    """
    asked = select(func.unnest(literal(sorted(uuids), ARRAY(Uuid))).label("uuid"))
    granted: list[Select[Any]] = [
        OBJECTS_OF_COLLECTION[collection](uuids).where(condition)
        for rule_collection, condition, fields in rules
        if rule_collection == collection and field in fields
    ]
    denied = asked.except_(*granted).subquery() if granted else asked.subquery()
    return select(
        literal(collection).label("collection"),
        denied.c.uuid.label("uuid"),
        literal(field).label("field"),
    )


async def access_load_fn(
    session: AsyncSession,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[AccessKey],
) -> list[bool]:
    """Whether the caller may read some fields of some objects, in one query.

    One select per field asked for of a collection, keeping, of the objects it
    is asked of, those matched by no rule of the caller's roles granting it.
    Only the accesses to deny come back, as the fields denied of each object:
    usually nothing at all.
    """
    rules = rules_of(sorted((await get_token()).realm_access.roles))
    denials = union_all(
        *(
            denied_select(collection, field, uuids, rules)
            for (collection, field), uuids in uuids_by_access(keys).items()
        )
    ).subquery()
    rows = await session.execute(
        select(
            denials.c.collection, denials.c.uuid, func.array_agg(denials.c.field)
        ).group_by(denials.c.collection, denials.c.uuid)
    )
    missing = {(collection, uuid): Fields(fields) for collection, uuid, fields in rows}
    return [
        field not in missing.get((collection, uuid), Fields())
        for collection, uuid, field in keys
    ]


def get_access_loaders(
    session: AsyncSession, get_token: Callable[[], Awaitable[Token]]
) -> dict[str, DataLoader]:
    """Return the dataloader deciding what the caller may read."""
    return {
        "access_loader": DataLoader(
            load_fn=partial(access_load_fn, session, get_token)
        ),
    }
