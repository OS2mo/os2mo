# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rule-based read access to specific fields of specific entities of a collection."""

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Container
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

from more_itertools import map_reduce
from sqlalchemy import ARRAY
from sqlalchemy import ColumnElement
from sqlalchemy import Select
from sqlalchemy import String
from sqlalchemy import Uuid
from sqlalchemy import any_
from sqlalchemy import column
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import union_all
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationRegistrering

# OIDC token role
Role: TypeAlias = str
# GraphQL collection
Collection: TypeAlias = str
# GraphQL field
Field: TypeAlias = str


class Rule(NamedTuple):
    """Grants read access to the fields on the collection under the condition."""

    role: Role
    collection: Collection
    condition: ColumnElement[bool]
    fields: frozenset[Field]


class AccessKey(NamedTuple):
    """A field access request."""

    collection: Collection
    uuid: UUID
    field: Field


# Each collection's model, holding the registrations of its objects.
# Every detail is an organisation function.
MODEL_OF_COLLECTION: dict[Collection, Any] = {
    "Address": OrganisationFunktionRegistrering,
    "Association": OrganisationFunktionRegistrering,
    "Class": KlasseRegistrering,
    "Employee": BrugerRegistrering,
    "Engagement": OrganisationFunktionRegistrering,
    "Facet": FacetRegistrering,
    "ITSystem": ITSystemRegistrering,
    "ITUser": OrganisationFunktionRegistrering,
    "KLE": OrganisationFunktionRegistrering,
    "Leave": OrganisationFunktionRegistrering,
    "Manager": OrganisationFunktionRegistrering,
    "Organisation": OrganisationRegistrering,
    "OrganisationUnit": OrganisationEnhedRegistrering,
    "Owner": OrganisationFunktionRegistrering,
    "RelatedUnit": OrganisationFunktionRegistrering,
    "RoleBinding": OrganisationFunktionRegistrering,
}


# The rules of every role. A caller's are those of their roles.
ROLE_POLICIES: list[Rule] = []


def load_rules(
    roles: Container[Role], collection: Collection, keys: Sequence[AccessKey]
) -> list[Rule]:
    """Load the relevant rules for the given collection, roles and fields."""
    accessed_fields = {key.field for key in keys}
    return [
        rule
        for rule in ROLE_POLICIES
        if rule.role in roles
        and rule.collection == collection
        and rule.fields & accessed_fields
    ]


def requested_select(keys: Iterable[AccessKey]) -> Select[Any]:
    """Select the requested accesses as rows of uuid and field."""
    # Unnesting the uuids and the fields side by side turns the accesses
    # [(uuid1, field1), (uuid1, field2), (uuid2, field1), ...]
    # into the rows:
    #
    #   uuid  | field
    #   ------+-------
    #   uuid1 | field1
    #   uuid1 | field2
    #   uuid2 | field1
    #   ...   | ...
    accesses = list({(key.uuid, key.field) for key in keys})
    rows = (
        func.unnest(
            literal([uuid for uuid, _ in accesses], ARRAY(Uuid)),
            literal([field for _, field in accesses], ARRAY(String)),
        )
        .table_valued(
            column("uuid", Uuid),
            column("field", String),
        )
        .render_derived()
    )
    return select(rows.c.uuid, rows.c.field)


def granted_select(rule: Rule, uuids: frozenset[UUID]) -> Select[Any]:
    """Select the accesses rule grants among uuids."""
    # Unnesting the fields across the matching objects turns the grant of
    # (field1, field2, ...) on uuid1, uuid2, ...
    # into the rows:
    #
    #   uuid  | field
    #   ------+-------
    #   uuid1 | field1
    #   uuid1 | field2
    #   uuid2 | field1
    #   uuid2 | field2
    #   ...   | ...
    model = MODEL_OF_COLLECTION[rule.collection]
    return select(
        model.uuid.label("uuid"),
        func.unnest(literal(list(rule.fields), ARRAY(String))).label("field"),
    ).where(
        model.uuid == any_(literal(list(uuids), ARRAY(Uuid))),
        rule.condition,
    )


def collection_denials(
    collection: Collection, keys: Sequence[AccessKey], roles: Container[Role]
) -> Select[Any]:
    """Select the accesses to collection that the roles' rules do not grant."""
    requested = requested_select(keys).cte()
    # Without a rule nothing is granted, so everything is denied
    denied = requested

    rules = load_rules(roles, collection, keys)
    if rules:
        asked = select(requested.c.uuid, requested.c.field)
        uuids = frozenset(key.uuid for key in keys)
        granted = union_all(*(granted_select(rule, uuids) for rule in rules)).cte()
        denied = asked.except_(select(granted.c.uuid, granted.c.field)).cte()

    return select(
        literal(collection).label("collection"),
        denied.c.uuid.label("uuid"),
        denied.c.field.label("field"),
    )


async def access_load_fn(
    session: AsyncSession,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[AccessKey],
) -> list[bool]:
    """Determine whether the requested field access is allowed."""
    roles = (await get_token()).realm_access.roles
    by_collection = map_reduce(keys, keyfunc=lambda key: key.collection)
    denied = union_all(
        *(
            collection_denials(collection, accesses, roles)
            for collection, accesses in by_collection.items()
        )
    ).subquery()
    rows = await session.execute(
        select(
            denied.c.collection, denied.c.uuid, func.array_agg(denied.c.field)
        ).group_by(denied.c.collection, denied.c.uuid)
    )
    missing: dict[tuple[Collection, UUID], frozenset[Field]] = {
        (collection, uuid): frozenset(fields) for collection, uuid, fields in rows
    }
    return [
        field not in missing.get((collection, uuid), frozenset())
        for collection, uuid, field in keys
    ]


def get_access_loaders(
    session: AsyncSession,
    get_token: Callable[[], Awaitable[Token]],
) -> dict[str, DataLoader]:
    """Return the dataloader deciding what the caller may read."""
    return {
        "access_loader": DataLoader(
            load_fn=partial(access_load_fn, session, get_token)
        ),
    }
