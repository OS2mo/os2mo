# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The policies: which objects may be read, and which of their fields.

Access is collection-based, not route-based: it does not matter how a
collection is reached, only what the caller may read of it. A collection is
anchored to the GraphQL types its objects are exposed through, and a policy
answers two independent questions about every object:

* may the caller read the object at all (the row predicate)
* which of its fields may they read (the field predicates)

Neither ever raises. A denied object is *removed* from the collection, or,
when the caller asks for `REDACT`, kept as a bare UUID whose content is
withheld: `current` is null and the temporal lists are empty. Removing is the
default, as redacting reveals that the objects exist.

Which of the two a caller wants depends on what they do with the answer. A
frontend shows what the user may see, and wants them gone. An integration
reconciling a downstream system must not mistake "you may not read this" for
"this was deleted", and wants them redacted, so that a missing UUID means the
object really is gone.

Only the address collection is expressed here so far, and only its row
predicate; a field without a predicate is readable whenever its object is.
The rest of the access still lives in the path-based `RBAC_MAP` and
`PUBLIC_FIELDS` of `mora.graphapi.rbac_map`.
"""

from collections import defaultdict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Collection
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import NamedTuple
from uuid import UUID

import strawberry
from sqlalchemy import ColumnElement
from sqlalchemy import distinct
from sqlalchemy import false
from sqlalchemy import select
from sqlalchemy import true

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import OrganisationFunktionRegistrering
from mora.graphapi.permissions import Collections

# The GraphQL types each collection's objects are read through: the objects
# themselves, and the bitemporal containers wrapping them.
COLLECTION_TYPES: dict[Collections, frozenset[str]] = {
    "address": frozenset({"Address", "AddressResponse", "AddressResponsePaged"}),
}

# Every type belonging to some collection
COLLECTION_TYPE_NAMES: frozenset[str] = frozenset(
    name for names in COLLECTION_TYPES.values() for name in names
)


@strawberry.enum(description="What to do with objects the policies deny.")
class Denied(Enum):
    REMOVE = "REMOVE"
    REDACT = "REDACT"


@dataclass(frozen=True)
class ObjectPermission:
    """What the caller may read of a single object."""

    # Whether the object may be read at all
    readable: bool
    # The restricted fields the caller may *not* read. Fields without a
    # predicate never appear here: they are readable with their object.
    denied_fields: frozenset[str] = frozenset()

    def withheld(self, requested: Collection[str]) -> frozenset[str]:
        """Which of the *requested* fields must be withheld.

        Empty when the object may be read as asked. An unreadable object
        withholds everything, so the requested fields come back whole.
        """
        if not self.readable:
            return frozenset(requested)
        return frozenset(requested) & self.denied_fields


@dataclass(frozen=True)
class Policy:
    """A collection's policy: which objects, and which of their fields."""

    # The objects the caller may read
    rows: ColumnElement[bool]
    # Per-field predicates. A field without one is readable whenever its
    # object is.
    fields: dict[str, ColumnElement[bool]] = field(default_factory=dict)


def address_policy(token: Token) -> Policy:
    """The addresses readable by the caller: all of them, to the reader.

    Without the role the collection is empty rather than forbidden: the
    caller may ask, and simply sees nothing.
    """
    if "reader" in token.realm_access.roles:
        return Policy(rows=true())
    return Policy(rows=false())


# The policy of each policy-guarded collection. The rest are still gated by
# the path-based `RBAC_MAP`.
POLICY_FOR: dict[str, Callable[[Token], Policy]] = {
    "address": address_policy,
}

# The column each collection's objects are identified by, which its
# predicates are expressed against.
IDENTIFIER_FOR: dict[str, Any] = {
    "address": OrganisationFunktionRegistrering.organisationfunktion_id,
}


async def permissions(
    session: AsyncSession, token: Token, collection: str, uuids: Iterable[UUID]
) -> dict[UUID, ObjectPermission]:
    """Resolve what the caller may read of each of *uuids*.

    One query for the objects, and one per restricted field, so resolving a
    page costs a handful of lookups rather than one per object.
    """
    uuids = list(uuids)
    if not uuids:
        return {}
    policy = POLICY_FOR[collection](token)
    identifier = IDENTIFIER_FOR[collection]

    async def matching(predicate: ColumnElement[bool]) -> set[UUID]:
        return set(
            (
                await session.scalars(
                    select(distinct(identifier)).where(predicate, identifier.in_(uuids))
                )
            ).all()
        )

    readable = await matching(policy.rows)
    permitted = {
        name: await matching(predicate) for name, predicate in policy.fields.items()
    }
    return {
        uuid: ObjectPermission(
            readable=uuid in readable,
            denied_fields=frozenset(
                name for name, allowed in permitted.items() if uuid not in allowed
            ),
        )
        for uuid in uuids
    }


class PolicyKey(NamedTuple):
    """A dataloader key: what may the caller read of this object."""

    collection: str
    uuid: UUID


def policy_loader(
    session: AsyncSession, get_token: Callable[[], Awaitable[Token]]
) -> Callable[[list[PolicyKey]], Awaitable[list[ObjectPermission]]]:
    """Batch permission lookups, grouped by collection.

    The loader is built per request, and its results are specific to the
    caller, so its lifetime must not be widened beyond one request.
    """

    async def load(keys: list[PolicyKey]) -> list[ObjectPermission]:
        token = await get_token()
        by_collection: dict[str, list[UUID]] = defaultdict(list)
        for key in keys:
            by_collection[key.collection].append(key.uuid)
        resolved: dict[PolicyKey, ObjectPermission] = {}
        for collection, uuids in by_collection.items():
            for uuid, permission in (
                await permissions(session, token, collection, uuids)
            ).items():
                resolved[PolicyKey(collection, uuid)] = permission
        return [resolved[key] for key in keys]

    return load
