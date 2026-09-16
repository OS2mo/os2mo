# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rule-based access to the mutators changing the objects a caller owns."""

from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from typing import Any
from typing import get_type_hints

from graphql import coerce_input_value
from more_itertools import one
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from strawberry import Schema
from strawberry.dataloader import DataLoader
from strawberry.types.arguments import convert_argument

from mora.config import Settings
from mora.db import AsyncSession
from mora.db import Policy
from mora.db import PolicyMutator
from mora.db import PolicySelector
from mora.db import PolicySelectorKind
from mora.graphapi import resolvers
from mora.graphapi.custom_schema import get_version
from mora.graphapi.policy import CheckSpec
from mora.graphapi.policy import Collection
from mora.graphapi.policy import MutatorRule
from mora.graphapi.policy import Role
from mora.graphapi.policy_cel import Activation
from mora.graphapi.policy_cel import evaluate_filter

# Each collection's predicate, selecting the objects a filter names
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


async def mutator_rules_load_fn(
    session: AsyncSession, keys: list[frozenset[Role]]
) -> list[list[MutatorRule]]:
    """The mutator rules of the policies the caller's roles name.

    A policy is the caller's while it is active and one of its selectors
    matches their roles. The loader is per request and the token does not
    change within one, so it is only ever asked about the one set of roles.
    """
    roles = one(keys)
    rows = await session.execute(
        select(PolicyMutator.name, PolicyMutator.condition, PolicyMutator.filter)
        .join(Policy)
        .where(Policy.active)
        .where(
            exists().where(
                PolicySelector.policy_fk == Policy.id,
                or_(
                    PolicySelector.kind == PolicySelectorKind.all,
                    and_(
                        PolicySelector.kind == PolicySelectorKind.role,
                        PolicySelector.value.in_(roles),
                    ),
                ),
            )
        )
    )
    return [[MutatorRule(*row) for row in rows]]


def get_policy_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    """Return the dataloader reading what the caller's policies grant."""
    return {
        "policy_loader": DataLoader(
            load_fn=partial(mutator_rules_load_fn, session), cache=True
        ),
    }


def named_objects(
    collection: Collection, filter: Any, settings: Settings, schema: Schema
) -> ColumnElement[bool]:
    """The objects of the collection a GraphQL filter names.

    The filter is coerced as the schema would coerce one written in a query,
    so the collection's own predicate decides which objects it names, and a
    rule reaches the same objects that filter would return.
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
