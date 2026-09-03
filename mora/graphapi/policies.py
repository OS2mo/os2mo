# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Read policies: which fields of which objects a caller may read.

Access is collection-based rather than route-based. It does not matter how
an object is reached, only what the caller may read of it, and that is
decided object by object: the union of the fields granted by the rules
matching it. Reading a field no rule grants fails, just like reading a field
no role grants.

Only the address collection is expressed here so far. Everything else is
still gated route by route in `mora.graphapi.rbac_map`.
"""

from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import NamedTuple
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import SQLColumnExpression
from sqlalchemy import distinct
from sqlalchemy import select

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import OrganisationFunktionRegistrering


@dataclass(frozen=True)
class Collection:
    name: str
    # The GraphQL types whose root is one of the collection's objects
    object_types: frozenset[str]
    # The types wrapping a page of them
    page_types: frozenset[str]
    # The column identifying the objects, which rules select them by
    identifier: SQLColumnExpression[UUID]

    @property
    def types(self) -> frozenset[str]:
        return self.object_types | self.page_types

    def enters(self, parent: str, returned: str) -> bool:
        """Whether a field from *parent* to *returned* leads into the collection."""
        return parent not in self.types and returned in self.types

    def is_object_field(self, parent: str, returned: str) -> bool:
        """Whether a field from *parent* to *returned* reads a field of an object.

        As opposed to leading further into the collection, through the
        containers and pages wrapping its objects.
        """
        return parent in self.object_types and returned not in self.types


ADDRESS = Collection(
    name="address",
    object_types=frozenset(
        {"Address", "AddressResponse", "AddressResponseRegistration"}
    ),
    page_types=frozenset({"AddressResponsePaged"}),
    identifier=OrganisationFunktionRegistrering.organisationfunktion_id,
)

COLLECTIONS: dict[str, Collection] = {ADDRESS.name: ADDRESS}

# The collection each of their GraphQL types belongs to
COLLECTION_OF_TYPE: dict[str, Collection] = {
    name: collection for collection in COLLECTIONS.values() for name in collection.types
}


@dataclass(frozen=True)
class Rule:
    """Grants reading *fields* of the *objects* of a collection.

    None stands for all of them: every field, or every object.
    """

    collection: str
    fields: frozenset[str] | None = None
    objects: ColumnElement[bool] | None = None

    def grants(self, field: str) -> bool:
        return self.fields is None or field in self.fields


@dataclass(frozen=True)
class Policy:
    rules: tuple[Rule, ...]


# The policy of each role. A caller's policies are those of their roles.
ROLE_POLICIES: dict[str, Policy] = {
    "reader": Policy(rules=(Rule(collection="address"),)),
}


def rules_for(token: Token, collection: str) -> list[Rule]:
    """The rules of the caller's policies for *collection*."""
    return [
        rule
        for role in sorted(token.realm_access.roles)
        if role in ROLE_POLICIES
        for rule in ROLE_POLICIES[role].rules
        if rule.collection == collection
    ]


@dataclass(frozen=True)
class Readable:
    """The fields a caller may read of one object; None means every field."""

    fields: frozenset[str] | None

    def __contains__(self, field: str) -> bool:
        return self.fields is None or field in self.fields

    def denies(self, fields: Iterable[str]) -> frozenset[str]:
        if self.fields is None:
            return frozenset()
        return frozenset(fields) - self.fields


async def readable(
    session: AsyncSession,
    rules: Iterable[Rule],
    collection: Collection,
    uuids: Sequence[UUID],
) -> dict[UUID, Readable]:
    """What *rules* grant of each object: the fields of the rules matching it.

    Costs one query per rule limited to some objects; the unconditional ones
    need none.
    """
    granted: dict[UUID, frozenset[str] | None] = {uuid: frozenset() for uuid in uuids}
    for rule in rules:
        matching: Sequence[UUID] = uuids
        if rule.objects is not None:
            matching = (
                await session.scalars(
                    select(distinct(collection.identifier)).where(
                        rule.objects, collection.identifier.in_(uuids)
                    )
                )
            ).all()
        for uuid in matching:
            fields = granted[uuid]
            if fields is None or rule.fields is None:
                granted[uuid] = None
            else:
                granted[uuid] = fields | rule.fields
    return {uuid: Readable(fields) for uuid, fields in granted.items()}


class PolicyKey(NamedTuple):
    collection: str
    uuid: UUID


def policy_loader(
    session: AsyncSession, get_token: Callable[[], Awaitable[Token]]
) -> Callable[[list[PolicyKey]], Awaitable[list[Readable]]]:
    """Batch the lookups of what the caller may read, by collection.

    The answers are the caller's, so the loader lives for one request only.
    """

    async def load(keys: list[PolicyKey]) -> list[Readable]:
        token = await get_token()
        by_collection: dict[str, list[UUID]] = defaultdict(list)
        for key in keys:
            by_collection[key.collection].append(key.uuid)
        loaded: dict[PolicyKey, Readable] = {}
        for name, uuids in by_collection.items():
            rules = rules_for(token, name)
            for uuid, fields in (
                await readable(session, rules, COLLECTIONS[name], uuids)
            ).items():
                loaded[PolicyKey(name, uuid)] = fields
        return [loaded[key] for key in keys]

    return load
