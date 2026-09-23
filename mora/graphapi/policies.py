# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rule-based access control to collections and mutators."""

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from typing import get_type_hints
from uuid import UUID

from graphql import coerce_input_value
from more_itertools import map_reduce
from pydantic import BaseModel
from pydantic import parse_obj_as
from sqlalchemy import ARRAY
from sqlalchemy import ColumnElement
from sqlalchemy import Select
from sqlalchemy import String
from sqlalchemy import Uuid
from sqlalchemy import and_
from sqlalchemy import any_
from sqlalchemy import column
from sqlalchemy import exists
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy import union_all
from strawberry.dataloader import DataLoader
from strawberry.types.arguments import convert_argument

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import Collection
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationRegistrering
from mora.db import Policy
from mora.db import PolicyReadRule
from mora.db import PolicyReadRuleField
from mora.db import PolicyWriteRule
from mora.graphapi import policy_cel
from mora.graphapi import resolvers
from mora.graphapi.custom_schema import CustomSchema
from mora.graphapi.graphql_utils import AccessKey
from mora.graphapi.graphql_utils import WriteKey
from mora.graphapi.policy_cel import CEL
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version

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


class WriteCondition(BaseModel):
    """Where to look for what a mutator requires, and what to look for."""

    collection: Collection
    filter: dict[str, Any]


class WriteRule(NamedTuple):
    """Grants the mutator, if the check of its arguments holds."""

    role: Role
    mutator: str
    check: Callable[[dict[str, Any]], ColumnElement[bool]]


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


# Each collection's corresponding predicate function.
# Organisation has no filter, so no rule can name anything but all of it.
PREDICATE_OF_COLLECTION: dict[Collection, Callable[..., ColumnElement]] = {
    Collection.Address: resolvers.address_predicate,
    Collection.Association: resolvers.association_predicate,
    Collection.Class: resolvers.class_predicate,
    Collection.Employee: resolvers.employee_predicate,
    Collection.Engagement: resolvers.engagement_predicate,
    Collection.Facet: resolvers.facet_predicate,
    Collection.ITSystem: resolvers.it_system_predicate,
    Collection.ITUser: resolvers.it_user_predicate,
    Collection.KLE: resolvers.kle_predicate,
    Collection.Leave: resolvers.leave_predicate,
    Collection.Manager: resolvers.manager_predicate,
    Collection.OrganisationUnit: resolvers.organisation_unit_predicate,
    Collection.Owner: resolvers.owner_predicate,
    Collection.RelatedUnit: resolvers.related_unit_predicate,
    Collection.RoleBinding: resolvers.rolebinding_predicate,
}


def parse_filter(
    schema: CustomSchema, collection: Collection, raw: dict[str, Any]
) -> Any:
    """Parse a filter dictionary into the strawberry filter of its collection.

    Args:
        schema: The GraphQL schema holding the filter types.
        collection: Selects the filter type within the schema.
        raw: The filter dictionary to be parsed.

    Raises:
        GraphQLError: When the filter is invalid, naming the value and where it
            sits within the filter.

    Returns:
        The dictionary, parsed into the collection's filter type.
    """
    filter = get_type_hints(PREDICATE_OF_COLLECTION[collection])["filter"]
    input_type = schema.schema_converter.from_input_object(filter)
    coerced = coerce_input_value(raw, input_type)
    return convert_argument(
        coerced,
        filter,
        scalar_registry=schema.schema_converter.scalar_registry,
        config=schema.config,
    )


def filter2predicate(
    settings: Settings,
    collection: Collection,
    graphql_version: Version,
    filter: dict[str, Any],
) -> ColumnElement[bool]:
    """Parse the filter of the collection into a clause."""
    predicate = PREDICATE_OF_COLLECTION[collection]
    parsed = parse_filter(get_schema(graphql_version), collection, filter)
    return predicate(settings=settings, version=graphql_version, filter=parsed)


def cel2predicate(
    settings: Settings,
    collection: Collection,
    graphql_version: Version,
    condition: CEL,
    token: Token,
) -> ColumnElement[bool]:
    """Evaluate the CEL condition into a filter, and the filter into a clause."""
    # No condition -> applies to all entities
    if not condition:
        return true()
    filter = policy_cel.evaluate(condition, token, {})
    return filter2predicate(settings, collection, graphql_version, filter)


def cel2check(
    settings: Settings,
    graphql_version: Version,
    condition: CEL,
    token: Token,
    args: dict[str, Any],
) -> ColumnElement[bool]:
    """Evaluate the CEL condition into a check that everything it names exists."""
    # No condition -> nothing has to exist
    if not condition:
        return true()
    yielded = policy_cel.evaluate(condition, token, args)
    if isinstance(yielded, bool):
        return true() if yielded else false()
    required = parse_obj_as(list[WriteCondition], yielded)
    # Allowing or denying outright is what true and false are for
    if not required:
        raise ValueError(
            f"condition {condition!r} requires nothing, yield true or false instead"
        )
    return and_(
        *(
            exists().where(
                filter2predicate(
                    settings,
                    requirement.collection,
                    graphql_version,
                    requirement.filter,
                )
            )
            for requirement in required
        )
    )


def write_check(
    mutator: str, args: dict[str, Any], rules: Iterable[WriteRule]
) -> ColumnElement[bool]:
    """The clause granting the mutator."""
    checks = [rule.check(args) for rule in rules if rule.mutator == mutator]
    # No rule names the mutator -> denied
    if not checks:
        return false()
    # Any rule granting the mutator is enough
    return or_(*checks)


def load_rules(
    collection: Collection, keys: Sequence[AccessKey], rules: Iterable[Rule]
) -> list[Rule]:
    """Return the relevant rules for the given collection and fields."""
    accessed_fields = {key.field for key in keys}
    return [
        rule
        for rule in rules
        if rule.collection == collection and rule.fields.intersection(accessed_fields)
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
    collection: Collection, keys: Sequence[AccessKey], rules: Iterable[Rule]
) -> Select[Any]:
    """Select the accesses to collection that the caller's rules do not grant."""
    requested = requested_select(keys).cte()
    # Without a rule nothing is granted, so everything is denied
    denied = requested

    rules = load_rules(collection, keys, rules)
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


async def policy_load_fn(
    session: AsyncSession,
    settings: Settings,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[int],
) -> list[list[Rule]]:
    """Load the rules of the active policies granted to the caller's roles."""
    token = await get_token()
    roles = token.realm_access.roles
    rows = await session.execute(
        select(
            Policy.role,
            PolicyReadRule.collection,
            PolicyReadRule.graphql_version,
            PolicyReadRule.condition,
            func.array_agg(PolicyReadRuleField.field),
        )
        .join(Policy.read_rules)
        .join(PolicyReadRule.fields)
        .where(
            Policy.role == any_(literal(roles, ARRAY(String))),
            Policy.active,
        )
        .group_by(
            Policy.role,
            PolicyReadRule.pk,
            PolicyReadRule.collection,
            PolicyReadRule.graphql_version,
            PolicyReadRule.condition,
        )
    )
    rules = [
        Rule(
            role=role,
            collection=collection,
            condition=cel2predicate(
                settings, collection, graphql_version, condition, token
            ),
            fields=frozenset(fields),
        )
        for role, collection, graphql_version, condition, fields in rows
    ]
    return [rules for _ in keys]


async def access_load_fn(
    session: AsyncSession,
    policy_loader: DataLoader[int, list[Rule]],
    keys: list[AccessKey],
) -> list[bool]:
    """Determine whether the requested field access is allowed."""
    # If this function is performing poorly, consider checking out 52d2a3fe,
    # c22dce95, 0aeca0fb and e3be669e
    rules = await policy_loader.load(0)
    by_collection = map_reduce(keys, keyfunc=lambda key: key.collection)
    denied = union_all(
        *(
            collection_denials(collection, accesses, rules)
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


async def write_policy_load_fn(
    session: AsyncSession,
    settings: Settings,
    get_token: Callable[[], Awaitable[Token]],
    keys: list[int],
) -> list[list[WriteRule]]:
    """Load the write rules of the active policies granted to the caller's roles."""
    token = await get_token()
    roles = token.realm_access.roles
    rows = await session.execute(
        select(
            Policy.role,
            PolicyWriteRule.mutator,
            PolicyWriteRule.graphql_version,
            PolicyWriteRule.condition,
        )
        .join(Policy.write_rules)
        .where(
            Policy.role == any_(literal(roles, ARRAY(String))),
            Policy.active,
        )
    )
    rules = [
        WriteRule(
            role=role,
            mutator=mutator,
            check=partial(cel2check, settings, graphql_version, condition, token),
        )
        for role, mutator, graphql_version, condition in rows
    ]
    return [rules for _ in keys]


async def write_load_fn(
    session: AsyncSession,
    write_policy_loader: DataLoader[int, list[WriteRule]],
    keys: list[WriteKey],
) -> list[bool]:
    """Determine whether the requested mutator access is allowed."""
    # If this function is performing poorly, consider checking out 0b7c0e5e
    rules = await write_policy_loader.load(0)
    checks = [write_check(mutator, args, rules) for mutator, args in keys]
    row = (await session.execute(select(*checks))).one()
    return [bool(granted) for granted in row]


def get_access_loaders(
    session: AsyncSession,
    settings: Settings,
    get_token: Callable[[], Awaitable[Token]],
) -> dict[str, DataLoader]:
    """Return the dataloaders deciding what the caller may read and write."""
    policy_loader: DataLoader[int, list[Rule]] = DataLoader(
        load_fn=partial(policy_load_fn, session, settings, get_token)
    )
    write_policy_loader: DataLoader[int, list[WriteRule]] = DataLoader(
        load_fn=partial(write_policy_load_fn, session, settings, get_token)
    )

    return {
        "access_loader": DataLoader(
            load_fn=partial(access_load_fn, session, policy_loader)
        ),
        "write_loader": DataLoader(
            load_fn=partial(write_load_fn, session, write_policy_loader),
            # The arguments are unhashable
            cache=False,
        ),
    }
