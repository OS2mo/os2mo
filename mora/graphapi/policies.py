# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections import defaultdict
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import Literal
from uuid import UUID

import strawberry
from cel_expr_python import cel  # type: ignore[import-untyped]
from graphql import coerce_input_value
from more_itertools import one
from pydantic import BaseModel
from pydantic import parse_raw_as
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
from strawberry.dataloader import DataLoader
from strawberry.types.arguments import convert_argument

from mora import db
from mora.db import AsyncSession
from mora.graphapi import resolvers
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.graphapi.policy_cel import CEL
from mora.graphapi.policy_cel import evaluate_filter
from mora.graphapi.policy_cel import validate_filter

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate

POLICY_LOADER_KEY = "policy_loader"


# The collections a check-spec may name, each the predicate selecting its
# matching objects. The filter is read off the predicate's own signature
COLLECTIONS: dict[str, Callable[..., ColumnElement]] = {
    "employee": resolvers.employee_predicate,
    "org_unit": resolvers.organisation_unit_predicate,
    "address": resolvers.address_predicate,
    "association": resolvers.association_predicate,
    "engagement": resolvers.engagement_predicate,
    "ituser": resolvers.it_user_predicate,
    "kle": resolvers.kle_predicate,
    "leave": resolvers.leave_predicate,
    "manager": resolvers.manager_predicate,
    "owner": resolvers.owner_predicate,
    "related_unit": resolvers.related_unit_predicate,
    "rolebinding": resolvers.rolebinding_predicate,
}


class CheckSpec(BaseModel):
    """One object a rule's filter requires to exist."""

    collection: Literal[tuple(COLLECTIONS)]  # type: ignore[valid-type]
    filter: dict[str, Any]

    class Config:
        extra = "forbid"

    @property
    def filter_type(self) -> type:
        """The MO filter type this spec's filter map is coerced into.

        The one the predicate takes, so the two cannot disagree.
        """
        return self.predicate.__annotations__["filter"]

    @property
    def predicate(self) -> Callable[..., ColumnElement]:
        """The collection's resolver predicate, selecting the matching objects."""
        return COLLECTIONS[self.collection]

    def to_filter(self, info: MOInfo) -> Any:
        """Convert the collection and filter dict to the resolver's filter type."""
        schema = info.schema
        coerce_input_value(
            self.filter, schema.schema_converter.from_input_object(self.filter_type)
        )
        return convert_argument(
            self.filter,
            self.filter_type,
            scalar_registry=schema.schema_converter.scalar_registry,
            config=schema.config,
        )


async def entity_filter_grants(
    filter: CEL, info: MOInfo, activation: cel.Activation
) -> bool:
    """Whether every check-spec the rule's `filter` yields matches an object."""
    specs = parse_raw_as(list[CheckSpec], evaluate_filter(filter, activation))
    if not specs:
        return False
    # Every spec must hold, AND-ed into one EXISTS statement so a bulk mutation
    # costs a single round trip
    matches = (
        exists().where(spec.predicate(info=info, filter=spec.to_filter(info)))
        for spec in specs
    )
    all_match = select(and_(*matches))
    return bool(await info.context.session.scalar(all_match))


async def policy_rules_resolver(
    session: AsyncSession, keys: list[frozenset[str]]
) -> list[dict[tuple[str, str], list[tuple[CEL, CEL]]]]:
    """The applicable rules for the caller's roles."""
    # The loader is cached per request, and the token never changes per request,
    # so we only ever get called with one set of roles
    roles = one(keys)
    query = (
        select(
            db.PolicyRule.type,
            db.PolicyRule.field,
            db.PolicyRule.condition,
            db.PolicyRule.filter,
        )
        .join(db.Policy)
        .where(db.Policy.active)
        .where(
            exists().where(
                db.PolicyActor.policy_fk == db.Policy.id,
                or_(
                    db.PolicyActor.kind == db.PolicyActorKind.all,
                    and_(
                        db.PolicyActor.kind == db.PolicyActorKind.role,
                        db.PolicyActor.value.in_(roles),
                    ),
                ),
            )
        )
    )
    rows = (await session.execute(query)).all()
    index: dict[tuple[str, str], list[tuple[CEL, CEL]]] = defaultdict(list)
    for row in rows:
        index[(row.type, row.field)].append((row.condition, row.filter))
    return [index]


def get_policy_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    return {
        POLICY_LOADER_KEY: DataLoader(load_fn=partial(policy_rules_resolver, session))
    }


PolicyActorKind = strawberry.enum(
    db.PolicyActorKind,
    description="The kind of actor attribute a policy matches on.",
)


@strawberry.input(
    description=(
        "Actor filter. Limits policies to those applicable to an actor with the "
        "given roles. A policy matches if it has at least one actor matching any "
        "of the provided roles (or an `all` actor)."
    )
)
class PolicyActorFilter:
    roles: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Actor role", "roles")
    )


@strawberry.input(description="Policy filter.")
class PolicyFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    names: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("name", "names")
    )
    active: bool | None = strawberry.field(
        default=None,
        description=(
            "Limit to policies with this activation state. When omitted or null, "
            "policies are not filtered by activation (set `true` for the "
            "currently-effective policies)."
        ),
    )
    actor: PolicyActorFilter | None = strawberry.field(
        default=None,
        description=(
            "Limit to policies applicable to an actor with these attributes. "
            "When omitted or null, policies are not filtered by actor."
        ),
    )


def _policy_actor_predicate(filter: PolicyActorFilter) -> ColumnElement:
    # Match by role. An absent (None) `roles` contributes nothing; an empty list
    # matches nothing. No roles provided (`{}`) means "has any actor" (existence
    # only).
    criteria: list[ColumnElement] = []
    if filter.roles is not None:
        criteria.append(
            and_(
                db.PolicyActor.kind == PolicyActorKind.role,
                db.PolicyActor.value.in_(filter.roles),
            )
        )
    if criteria:
        # An "all" actor matches every actor, so a policy with one satisfies any
        # role-based actor filter.
        criteria.append(db.PolicyActor.kind == PolicyActorKind.all)
        inner = or_(*criteria)
    else:
        # No roles provided (`{}`) means "has any actor" (existence only), which
        # already includes "all" actors.
        inner = true()
    return exists().where(db.PolicyActor.policy_fk == db.Policy.id).where(inner)


def policy_predicate(filter: PolicyFilter) -> ColumnElement:
    predicates: list[ColumnElement] = [true()]

    if filter.uuids is not None:
        predicates.append(db.Policy.id.in_(filter.uuids))

    if filter.names is not None:
        predicates.append(db.Policy.name.in_(filter.names))

    if filter.active is not None:
        predicates.append(db.Policy.active == filter.active)

    if filter.actor is not None:
        predicates.append(_policy_actor_predicate(filter.actor))

    return and_(*predicates)


@strawberry.type(description="An actor a policy applies to.")
class PolicyActor:
    uuid: UUID = strawberry.field(description="UUID of the actor binding.")
    kind: PolicyActorKind = strawberry.field(
        description="The kind of attribute matched on."
    )
    value: str = strawberry.field(description="The value the attribute must equal.")


@strawberry.type(
    description=(
        "A resource a policy grants access to, expressed GraphQL-natively as a "
        "(type, field) pair."
    )
)
class PolicyRule:
    uuid: UUID = strawberry.field(description="UUID of the rule.")
    type: str = strawberry.field(
        description=(
            "GraphQL type the rule grants access to: a collection's object "
            'type, or "Query"/"Mutation".'
        )
    )
    field: str = strawberry.field(
        description='Field (or mutator) on the type, or "*" for all fields.'
    )
    condition: str = strawberry.field(
        description=(
            "CEL condition that must evaluate true for the rule to "
            'grant access. The empty string means the rule is unconditional.'
        )
    )
    filter: str = strawberry.field(
        description=(
            "CEL expression returning one or more access-check specs "
            "`{collection, filter}`, each run as a SQL existence check; the "
            "rule only grants when all of them pass. The empty string means "
            "no entity restriction."
        )
    )


@strawberry.type(
    description=(
        "An access policy. A policy applies to a collection of actors and "
        "grants them access to a number of resources."
    )
)
class Policy:
    uuid: UUID = strawberry.field(description="UUID of the policy.")
    name: str = strawberry.field(description="Name of the policy.")
    description: str = strawberry.field(description="Description of the policy.")
    active: bool = strawberry.field(description="Whether the policy is in effect.")

    @strawberry.field(description="Actors this policy applies to.")
    async def actors(root: "Policy", info: MOInfo) -> list[PolicyActor]:
        session: AsyncSession = info.context.session
        result = await session.scalars(
            select(db.PolicyActor)
            .where(db.PolicyActor.policy_fk == root.uuid)
            .order_by(db.PolicyActor.pk)
        )
        return [
            PolicyActor(uuid=actor.pk, kind=actor.kind, value=actor.value)
            for actor in result
        ]

    @strawberry.field(description="Resources this policy grants access to.")
    async def rules(root: "Policy", info: MOInfo) -> list[PolicyRule]:
        session: AsyncSession = info.context.session
        result = await session.scalars(
            select(db.PolicyRule)
            .where(db.PolicyRule.policy_fk == root.uuid)
            .order_by(db.PolicyRule.pk)
        )
        return [to_policy_rule(rule) for rule in result]


def to_policy_rule(rule: "db.PolicyRule") -> PolicyRule:
    return PolicyRule(
        uuid=rule.pk,
        type=rule.type,
        field=rule.field,
        condition=rule.condition,
        filter=rule.filter,
    )


def to_policy(policy: "db.Policy") -> Policy:
    return Policy(
        uuid=policy.id,
        name=policy.name,
        description=policy.description,
        active=policy.active,
    )


async def policy_resolver(
    info: MOInfo,
    filter: PolicyFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = PolicyFilter()

    predicate = policy_predicate(filter=filter)
    query = select(db.Policy.id).where(predicate).order_by(db.Policy.id)
    session: AsyncSession = info.context.session
    uuids, next_cursor = await paginate(session, query, db.Policy.id, limit, cursor)

    result = await session.scalars(
        select(db.Policy).where(db.Policy.id.in_(uuids)).order_by(db.Policy.id)
    )
    return ObjectsAndCursor(
        objects=[to_policy(policy) for policy in result],
        next_cursor=next_cursor,
    )


def validate_rule_filter(filter: CEL) -> None:
    """Reject a rule `filter` that is not a compilable CEL expression.

    Any rule may carry a filter. The filter is a CEL expression returning one
    or more check-specs; its result shape depends on runtime variables
    (`token`/`settings`/`args`), so declare time only compile-checks it. A
    compilable expression that yields a non-check-spec fails hard at
    permission-check time (see `entity_filter_grants`).
    """
    # The empty string means "no filter", so there is nothing to compile
    if not filter:
        return
    validate_filter(filter)
