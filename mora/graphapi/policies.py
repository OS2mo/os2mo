# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rule-based read access to specific fields of specific entities of a collection."""

from collections.abc import Callable
from collections.abc import Container
from collections.abc import Iterable
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import get_type_hints
from uuid import UUID

from graphql import coerce_input_value
from more_itertools import map_reduce
from sqlalchemy import ARRAY
from sqlalchemy import ColumnElement
from sqlalchemy import CompoundSelect
from sqlalchemy import Select
from sqlalchemy import String
from sqlalchemy import Uuid
from sqlalchemy import and_
from sqlalchemy import column
from sqlalchemy import exists
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy import union_all
from sqlalchemy.orm import selectinload
from strawberry import Schema
from strawberry.dataloader import DataLoader
from strawberry.types.arguments import convert_argument

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationRegistrering
from mora.db import Policy
from mora.db import PolicyReader
from mora.db import PolicySelector
from mora.db import PolicySelectorKind
from mora.graphapi import resolvers
from mora.graphapi.custom_schema import get_version
from mora.graphapi.policy import AccessKey
from mora.graphapi.policy import CheckSpec
from mora.graphapi.policy import Collection
from mora.graphapi.policy import Field
from mora.graphapi.policy import MutatorRule
from mora.graphapi.policy import ReadRule
from mora.graphapi.policy import Role
from mora.graphapi.policy import Rules
from mora.graphapi.policy_cel import Activation
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import check_condition
from mora.graphapi.policy_cel import evaluate_filter

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


# Each collection's predicate, selecting the objects a filter names.
# `Organisation` has none: there is one root organisation, and nothing to name
PREDICATE_OF_COLLECTION: dict[Collection, Callable[..., ColumnElement]] = {
    "Address": resolvers.address_predicate,
    "Association": resolvers.association_predicate,
    "Class": resolvers.class_predicate,
    "Employee": resolvers.employee_predicate,
    "Engagement": resolvers.engagement_predicate,
    "Facet": resolvers.facet_predicate,
    "ITSystem": resolvers.it_system_predicate,
    "ITUser": resolvers.it_user_predicate,
    "KLE": resolvers.kle_predicate,
    "Leave": resolvers.leave_predicate,
    "Manager": resolvers.manager_predicate,
    "OrganisationUnit": resolvers.organisation_unit_predicate,
    "Owner": resolvers.owner_predicate,
    "RelatedUnit": resolvers.related_unit_predicate,
    "RoleBinding": resolvers.rolebinding_predicate,
}


def selects(selector: PolicySelector, roles: Container[Role]) -> bool:
    """Whether the selector matches a caller holding the roles."""
    if selector.kind is PolicySelectorKind.all:
        return True
    return selector.value in roles


def named_objects(
    collection: Collection,
    filter: Any,
    settings: Settings,
    schema: Schema,
) -> ColumnElement[bool]:
    """The objects of the collection a GraphQL filter names.

    The filter is coerced as the schema would coerce one written in a query,
    so the collection's own predicate decides which objects it names, and the
    caller gets the same objects that filter would return.
    """
    if collection not in PREDICATE_OF_COLLECTION:
        raise ValueError(f"A filter cannot name the objects of {collection}")
    predicate = PREDICATE_OF_COLLECTION[collection]
    filter_type = get_type_hints(predicate)["filter"]
    coerced = coerce_input_value(
        filter, schema.schema_converter.from_input_object(filter_type)
    )
    return predicate(
        settings=settings,
        version=get_version(schema),
        filter=convert_argument(
            coerced,
            filter_type,
            scalar_registry=schema.schema_converter.scalar_registry,
            config=schema.config,
        ),
    )


def reached_objects(
    reader: PolicyReader,
    settings: Settings,
    schema: Schema,
    activation: Activation,
) -> ColumnElement[bool]:
    """The objects a reader reaches: the ones its filter names.

    A reader carrying no filter reaches every object of its collection.
    """
    if not reader.filter:
        return true()
    return named_objects(
        reader.collection,
        evaluate_filter(reader.filter, activation),
        settings,
        schema,
    )


def as_spec(spec: Any) -> CheckSpec:
    """The check spec a mutator rule's filter names."""
    match spec:
        case {"collection": str(collection), "filter": dict(filter)}:
            return CheckSpec(collection, filter)
    raise ValueError(f"A mutator rule names no object in {spec!r}")


def owned_objects(
    rules: Iterable[MutatorRule],
    settings: Settings,
    schema: Schema,
    activation: Activation,
) -> ColumnElement[bool] | None:
    """What the caller must own for one of the rules to grant the mutator.

    A rule requires every object its filter names, and the rules of a mutator
    are alternatives, so any one of them granting is enough. A rule naming
    nothing requires an object that does not exist, so it grants nothing, and
    None is the answer when no rule is left to grant anything.
    """
    owned = []
    for rule in rules:
        specs = [as_spec(spec) for spec in evaluate_filter(rule.filter, activation)]
        if not specs:
            continue
        owned.append(
            and_(
                *(
                    exists().where(
                        named_objects(spec.collection, spec.filter, settings, schema)
                    )
                    for spec in specs
                )
            )
        )
    if not owned:
        return None
    return or_(*owned)


async def load_rules(
    session: AsyncSession, token: Token, settings: Settings, schema: Schema
) -> Rules:
    """Load what the caller's policies grant them.

    A policy is the caller's while it is active and one of its selectors
    matches their roles. Its readers are then theirs, save those whose
    condition they do not pass, and so are its mutators.
    """
    policies = await session.scalars(
        select(Policy)
        .where(Policy.active)
        .options(
            selectinload(Policy.selectors),
            selectinload(Policy.readers),
            selectinload(Policy.mutators),
        )
    )
    # The rules are read before any field is resolved, so no field has arguments
    activation = build_activation(token, settings, {})
    roles = token.realm_access.roles
    held = [
        policy
        for policy in policies
        if any(selects(selector, roles) for selector in policy.selectors)
    ]
    return Rules(
        read=[
            ReadRule(
                collection=reader.collection,
                condition=reached_objects(reader, settings, schema, activation),
                fields=frozenset(reader.fields),
            )
            for policy in held
            for reader in policy.readers
            if check_condition(reader.condition, activation)
        ],
        mutators=[
            MutatorRule(
                name=mutator.name, condition=mutator.condition, filter=mutator.filter
            )
            for policy in held
            for mutator in policy.mutators
        ],
    )


def rules_deciding(
    rules: Iterable[ReadRule], collection: Collection, keys: Sequence[AccessKey]
) -> list[ReadRule]:
    """The caller's rules for the given collection and fields."""
    accessed_fields = {key.field for key in keys}
    return [
        rule
        for rule in rules
        if rule.collection == collection and rule.fields & accessed_fields
    ]


def rules_granting(rules: Sequence[ReadRule], field: Field) -> frozenset[ReadRule]:
    """The rules granting the field."""
    return frozenset(rule for rule in rules if field in rule.fields)


def denied_select(
    collection: Collection, accesses: Sequence[AccessKey], rules: Iterable[ReadRule]
) -> Select[Any]:
    """Select the accesses to deny among accesses that the same rules grant.

    A rule granting one of the fields grants them all, so one test per object
    answers for every field, and the fields are expanded onto the objects no
    rule granted.
    """
    uuids = literal(list({access.uuid for access in accesses}), ARRAY(Uuid))
    fields = literal(list({access.field for access in accesses}), ARRAY(String))
    model = MODEL_OF_COLLECTION[collection]

    asked = func.unnest(uuids).table_valued(column("uuid", Uuid)).render_derived()
    # The disjunction of no conditions is false: without a rule, nothing is granted
    granted = select(1).where(
        model.uuid == asked.c.uuid,
        or_(false(), *(rule.condition for rule in rules)),
    )
    denied = select(asked.c.uuid).where(~granted.exists()).subquery()

    return select(
        literal(collection).label("collection"),
        denied.c.uuid.label("uuid"),
        func.unnest(fields).label("field"),
    )


def collection_denials(
    rules: Iterable[ReadRule], collection: Collection, keys: Sequence[AccessKey]
) -> CompoundSelect:
    """Select the accesses to collection the caller's rules do not grant.

    Whether a field is denied an object turns on the rules granting it, never
    on the field itself, so the accesses are grouped by those rules and one
    select decides each group.
    """
    deciding = rules_deciding(rules, collection, keys)
    by_rules = map_reduce(keys, keyfunc=lambda key: rules_granting(deciding, key.field))
    return union_all(
        *(
            denied_select(collection, accesses, granting)
            for granting, accesses in by_rules.items()
        )
    )


async def access_load_fn(
    session: AsyncSession, rules: Sequence[ReadRule], keys: list[AccessKey]
) -> list[bool]:
    """Determine whether the requested field access is allowed."""
    by_collection = map_reduce(keys, keyfunc=lambda key: key.collection)
    denied = union_all(
        *(
            collection_denials(rules, collection, accesses)
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


def get_access_loader(
    session: AsyncSession, rules: Sequence[ReadRule]
) -> DataLoader[AccessKey, bool]:
    """Return the dataloader deciding what the caller may read."""
    return DataLoader(load_fn=partial(access_load_fn, session, rules))
