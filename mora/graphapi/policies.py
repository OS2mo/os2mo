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
from sqlalchemy import true
from sqlalchemy import union_all
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import Collection
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationRegistrering

# OIDC token role
Role: TypeAlias = str
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
    Collection.Address: OrganisationFunktionRegistrering,
    Collection.Association: OrganisationFunktionRegistrering,
    Collection.Class: KlasseRegistrering,
    Collection.Employee: BrugerRegistrering,
    Collection.Engagement: OrganisationFunktionRegistrering,
    Collection.Facet: FacetRegistrering,
    Collection.ITSystem: ITSystemRegistrering,
    Collection.ITUser: OrganisationFunktionRegistrering,
    Collection.KLE: OrganisationFunktionRegistrering,
    Collection.Leave: OrganisationFunktionRegistrering,
    Collection.Manager: OrganisationFunktionRegistrering,
    Collection.Organisation: OrganisationRegistrering,
    Collection.OrganisationUnit: OrganisationEnhedRegistrering,
    Collection.Owner: OrganisationFunktionRegistrering,
    Collection.RelatedUnit: OrganisationFunktionRegistrering,
    Collection.RoleBinding: OrganisationFunktionRegistrering,
}


# The rules of every role. A caller's are those of their roles.
ROLE_POLICIES: list[Rule] = [
    Rule(
        role="reader",
        collection=Collection.Address,
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
    Rule(
        role="reader",
        collection=Collection.Association,
        condition=true(),
        fields=frozenset(
            {
                "association_type",
                "association_type_response",
                "association_type_uuid",
                "dynamic_class",
                "dynamic_class_response",
                "dynamic_class_uuid",
                "employee",
                "employee_uuid",
                "it_user",
                "it_user_response",
                "it_user_uuid",
                "job_function",
                "job_function_response",
                "job_function_uuid",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "person",
                "person_response",
                "primary",
                "primary_response",
                "primary_uuid",
                "substitute",
                "substitute_response",
                "substitute_uuid",
                "trade_union",
                "trade_union_response",
                "trade_union_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Class,
        condition=true(),
        fields=frozenset(
            {
                "children",
                "children_response",
                "description",
                "example",
                "facet",
                "facet_response",
                "facet_uuid",
                "full_name",
                "it_system",
                "it_system_response",
                "it_system_uuid",
                "name",
                "org_uuid",
                "owner",
                "owner_response",
                "parent",
                "parent_response",
                "parent_uuid",
                "published",
                "scope",
                "top_level_facet",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Employee,
        condition=true(),
        fields=frozenset(
            {
                "addresses",
                "addresses_response",
                "associations",
                "associations_response",
                "cpr_no",
                "cpr_number",
                "engagements",
                "engagements_response",
                "given_name",
                "givenname",
                "itusers",
                "itusers_response",
                "leaves",
                "leaves_response",
                "manager_roles",
                "manager_roles_response",
                "name",
                "nickname",
                "nickname_given_name",
                "nickname_givenname",
                "nickname_surname",
                "seniority",
                "surname",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Engagement,
        condition=true(),
        fields=frozenset(
            {
                "addresses_response",
                "employee",
                "employee_uuid",
                "engagement_type",
                "engagement_type_response",
                "engagement_type_uuid",
                "extension_1",
                "extension_10",
                "extension_2",
                "extension_3",
                "extension_4",
                "extension_5",
                "extension_6",
                "extension_7",
                "extension_8",
                "extension_9",
                "fraction",
                "is_primary",
                "itusers",
                "itusers_response",
                "job_function",
                "job_function_response",
                "job_function_uuid",
                "leave",
                "leave_response",
                "leave_uuid",
                "managers",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "person",
                "person_response",
                "primary",
                "primary_response",
                "primary_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Facet,
        condition=true(),
        fields=frozenset(
            {
                "children",
                "children_response",
                "classes",
                "classes_responses",
                "description",
                "org_uuid",
                "parent",
                "parent_response",
                "parent_uuid",
                "published",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.ITSystem,
        condition=true(),
        fields=frozenset(
            {
                "name",
                "roles",
                "roles_response",
                "system_type",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.ITUser,
        condition=true(),
        fields=frozenset(
            {
                "addresses",
                "addresses_response",
                "binding_type",
                "employee",
                "employee_uuid",
                "engagement",
                "engagement_response",
                "engagement_uuid",
                "engagement_uuids",
                "engagements",
                "engagements_responses",
                "external_id",
                "itsystem",
                "itsystem_response",
                "itsystem_uuid",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "person",
                "person_response",
                "primary",
                "primary_response",
                "primary_uuid",
                "rolebindings",
                "rolebindings_response",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.KLE,
        condition=true(),
        fields=frozenset(
            {
                "kle_aspect_uuids",
                "kle_aspects",
                "kle_aspects_response",
                "kle_number",
                "kle_number_response",
                "kle_number_uuid",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Leave,
        condition=true(),
        fields=frozenset(
            {
                "employee",
                "employee_uuid",
                "engagement",
                "engagement_response",
                "engagement_uuid",
                "leave_type",
                "leave_type_response",
                "leave_type_uuid",
                "person",
                "person_response",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Manager,
        condition=true(),
        fields=frozenset(
            {
                "employee",
                "employee_uuid",
                "engagement_response",
                "manager_level",
                "manager_level_response",
                "manager_level_uuid",
                "manager_type",
                "manager_type_response",
                "manager_type_uuid",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "person",
                "person_response",
                "responsibilities",
                "responsibilities_response",
                "responsibility_uuids",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Organisation,
        condition=true(),
        fields=frozenset(
            {
                "municipality_code",
                "name",
                "type",
                "user_key",
                "uuid",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.OrganisationUnit,
        condition=true(),
        fields=frozenset(
            {
                "addresses",
                "addresses_response",
                "ancestors",
                "associations",
                "associations_response",
                "child_count",
                "children",
                "children_response",
                "engagements",
                "engagements_response",
                "has_children",
                "itusers",
                "itusers_response",
                "kles",
                "kles_response",
                "leaves",
                "leaves_response",
                "managers",
                "managers_response",
                "name",
                "org_unit_hierarchy",
                "org_unit_hierarchy_model",
                "org_unit_level",
                "org_unit_level_uuid",
                "owners",
                "parent",
                "parent_response",
                "parent_uuid",
                "related_units",
                "related_units_response",
                "root",
                "root_response",
                "time_planning",
                "time_planning_response",
                "time_planning_uuid",
                "type",
                "unit_hierarchy_response",
                "unit_level_response",
                "unit_type",
                "unit_type_response",
                "unit_type_uuid",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.Owner,
        condition=true(),
        fields=frozenset(
            {
                "employee_uuid",
                "org_unit",
                "org_unit_response",
                "org_unit_uuid",
                "owner",
                "owner_inference_priority",
                "owner_response",
                "owner_uuid",
                "person",
                "person_response",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.RelatedUnit,
        condition=true(),
        fields=frozenset(
            {
                "org_unit_uuids",
                "org_units",
                "org_units_response",
                "type",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
    Rule(
        role="reader",
        collection=Collection.RoleBinding,
        condition=true(),
        fields=frozenset(
            {
                "ituser",
                "ituser_response",
                "org_unit",
                "org_unit_response",
                "role",
                "role_response",
                "user_key",
                "uuid",
                "validity",
            }
        ),
    ),
]


def load_rules(
    collection: Collection,
    keys: Sequence[AccessKey],
    roles: Container[Role],
    rules: Iterable[Rule],
) -> list[Rule]:
    """Return the relevant rules for the given collection and fields."""
    accessed_fields = {key.field for key in keys}
    return [
        rule
        for rule in rules
        if rule.role in roles
        and rule.collection == collection
        and rule.fields.intersection(accessed_fields)
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
    collection: Collection,
    keys: Sequence[AccessKey],
    roles: Container[Role],
    rules: Iterable[Rule],
) -> Select[Any]:
    """Select the accesses to collection that the roles' rules do not grant."""
    requested = requested_select(keys).cte()
    # Without a rule nothing is granted, so everything is denied
    denied = requested

    rules = load_rules(collection, keys, roles, rules)
    if rules:
        asked = select(requested.c.uuid, requested.c.field)
        uuids = frozenset(key.uuid for key in keys)
        granted = union_all(*(granted_select(rule, uuids) for rule in rules)).cte()
        denied = asked.except_(select(granted.c.uuid, granted.c.field)).cte()

    return select(
        literal(collection.value, String).label("collection"),
        denied.c.uuid.label("uuid"),
        denied.c.field.label("field"),
    )


async def access_load_fn(
    session: AsyncSession,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[AccessKey],
) -> list[bool]:
    """Determine whether the requested field access is allowed."""
    # If this function is performing poorly, consider checking out 52d2a3fe
    # and c22dce95
    roles = (await get_token()).realm_access.roles
    rules = ROLE_POLICIES
    by_collection = map_reduce(keys, keyfunc=lambda key: key.collection)
    denied = union_all(
        *(
            collection_denials(collection, accesses, roles, rules)
            for collection, accesses in by_collection.items()
        )
    ).subquery()
    rows = await session.execute(
        select(
            denied.c.collection, denied.c.uuid, func.array_agg(denied.c.field)
        ).group_by(denied.c.collection, denied.c.uuid)
    )
    # The collection comes back as the plain string it was selected as
    missing: dict[tuple[Collection, UUID], frozenset[Field]] = {
        (Collection(collection), uuid): frozenset(fields)
        for collection, uuid, fields in rows
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
