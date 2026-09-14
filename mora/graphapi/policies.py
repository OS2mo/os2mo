# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rule-based read access to specific fields of specific entities of a collection."""

from collections import defaultdict
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
from sqlalchemy import CompoundSelect
from sqlalchemy import Select
from sqlalchemy import String
from sqlalchemy import Uuid
from sqlalchemy import any_
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
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
ROLE_POLICIES: list[Rule] = [
    Rule(
        role="reader",
        collection="Address",
        condition=true(),
        fields=frozenset(
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
    ),
]


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


def rules_granting(rules: Sequence[Rule], field: Field) -> tuple[int, ...]:
    """The rules granting reading field, by their index."""
    return tuple(index for index, rule in enumerate(rules) if field in rule.fields)


def accesses_by_rules(
    keys: Iterable[AccessKey], rules: Sequence[Rule]
) -> dict[frozenset[Field], frozenset[UUID]]:
    """The objects asked about, by the fields asked of them that the same rules grant.

    Whether a field is denied an object turns on the rules granting it, never
    on the field itself, so the fields the same rules grant are decided
    together: one test of an object answers for all of them.
    """
    grouped: dict[tuple[int, ...], tuple[set[Field], set[UUID]]] = defaultdict(
        lambda: (set(), set())
    )
    for _, uuid, field in keys:
        fields, uuids = grouped[rules_granting(rules, field)]
        fields.add(field)
        uuids.add(uuid)
    return {frozenset(fields): frozenset(uuids) for fields, uuids in grouped.values()}


def denied_select(
    collection: Collection,
    fields: frozenset[Field],
    uuids: frozenset[UUID],
    conditions: Sequence[ColumnElement[bool]],
) -> Select[Any]:
    """Select the accesses to deny among reading fields of uuids.

    The objects asked about, less those matching a rule granting the fields.
    The rules add a condition each to the objects' rows, so their disjunction
    stands for all of them, and the fields they grant are expanded from the one
    select rather than selected one by one.
    """
    uuid_array = literal(list(uuids), ARRAY(Uuid))
    model = MODEL_OF_COLLECTION[collection]
    # The disjunction of no conditions is false: without a rule, nothing is granted
    granted = select(model.uuid).where(
        model.uuid == any_(uuid_array),
        or_(false(), *conditions),
    )
    denied = select(func.unnest(uuid_array).label("uuid")).except_(granted).subquery()
    return select(
        literal(collection).label("collection"),
        denied.c.uuid.label("uuid"),
        func.unnest(literal(list(fields), ARRAY(String))).label("field"),
    )


def collection_denials(
    collection: Collection, keys: Sequence[AccessKey], roles: Container[Role]
) -> CompoundSelect:
    """Select the accesses to collection the roles' rules do not grant.

    One select per set of fields the same rules grant, deciding them on the
    objects they were asked of under the rules granting all of them: the fields
    were grouped by the rules granting them, so a rule granting one grants all.
    """
    rules = load_rules(roles, collection, keys)
    return union_all(
        *(
            denied_select(
                collection,
                fields,
                uuids,
                [rule.condition for rule in rules if fields <= rule.fields],
            )
            for fields, uuids in accesses_by_rules(keys, rules).items()
        )
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
