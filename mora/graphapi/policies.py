# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from collections.abc import Collection
from datetime import datetime
from uuid import UUID

import strawberry
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true

from mora import db
from mora.auth.keycloak.models import Token
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.util import now

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate


@strawberry.enum(description="The kind of actor attribute a policy matches on.")
class PolicyActorKind(enum.Enum):
    uuid = "uuid"
    username = "username"
    role = "role"


@strawberry.input(
    description=(
        "Actor filter. Limits policies to those applicable to an actor with the "
        "given attributes. A policy matches if it has at least one actor matching "
        "any of the provided attributes (uuids, usernames or roles)."
    )
)
class PolicyActorFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Actor UUID", "uuids")
    )
    usernames: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Actor username", "usernames")
    )
    roles: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Actor role", "roles")
    )


@strawberry.input(description="Policy filter.")
class PolicyFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    start: datetime | None = strawberry.field(
        default=None,
        description=(
            "Only return policies whose validity has not ended before this "
            "point. Combine with `end` to limit to policies valid in an "
            "interval (e.g. set both to 'now' for currently-valid policies)."
        ),
    )
    end: datetime | None = strawberry.field(
        default=None,
        description="Only return policies that have started by this point.",
    )
    actor: PolicyActorFilter | None = strawberry.field(
        default=None,
        description=(
            "Limit to policies applicable to an actor with these attributes. "
            "When omitted or null, policies are not filtered by actor."
        ),
    )


def _policy_actor_predicate(filter: PolicyActorFilter) -> ColumnElement:
    # Build an OR of the provided actor attributes. Each absent (None) field
    # contributes nothing; an empty list matches nothing for that attribute. No
    # attributes provided (`{}`) means "has any actor" (existence only).
    criteria: list[ColumnElement] = []
    if filter.uuids is not None:
        criteria.append(
            and_(
                db.PolicyActor.kind == PolicyActorKind.uuid.value,
                db.PolicyActor.value.in_([str(uuid) for uuid in filter.uuids]),
            )
        )
    if filter.usernames is not None:
        criteria.append(
            and_(
                db.PolicyActor.kind == PolicyActorKind.username.value,
                db.PolicyActor.value.in_(filter.usernames),
            )
        )
    if filter.roles is not None:
        criteria.append(
            and_(
                db.PolicyActor.kind == PolicyActorKind.role.value,
                db.PolicyActor.value.in_(filter.roles),
            )
        )
    inner = or_(*criteria) if criteria else true()
    return exists().where(db.PolicyActor.policy_fk == db.Policy.id).where(inner)


def policy_predicate(info: MOInfo, filter: PolicyFilter) -> ColumnElement:
    predicates: list[ColumnElement] = [true()]

    if filter.uuids is not None:
        predicates.append(db.Policy.id.in_(filter.uuids))

    # Validity overlap: a policy is valid over [start, end) (a null end means
    # open-ended), so it overlaps the queried [filter.start, filter.end] window
    # when it started by `end` and has not ended before `start`.
    if filter.start is not None:
        predicates.append(or_(db.Policy.end.is_(None), db.Policy.end >= filter.start))
    if filter.end is not None:
        predicates.append(db.Policy.start <= filter.end)

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


@strawberry.type(
    description=(
        "An access policy. A policy applies to a collection of actors and "
        "grants them access to a number of resources."
    )
)
class Policy:
    uuid: UUID = strawberry.field(description="UUID of the policy.")
    name: str = strawberry.field(description="Name of the policy.")
    description: str | None = strawberry.field(description="Description of the policy.")
    start: datetime = strawberry.field(description="Start of the policy's validity.")
    end: datetime | None = strawberry.field(
        description="End of the policy's validity, if applicable."
    )

    @strawberry.field(description="Actors this policy applies to.")
    async def actors(root: "Policy", info: MOInfo) -> list[PolicyActor]:
        session: AsyncSession = info.context.session
        result = await session.scalars(
            select(db.PolicyActor)
            .where(db.PolicyActor.policy_fk == root.uuid)
            .order_by(db.PolicyActor.pk)
        )
        return [
            PolicyActor(
                uuid=actor.pk, kind=PolicyActorKind(actor.kind), value=actor.value
            )
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
        return [
            PolicyRule(uuid=rule.pk, type=rule.type, field=rule.field)
            for rule in result
        ]


def _to_policy(policy: "db.Policy") -> Policy:
    return Policy(
        uuid=policy.id,
        name=policy.name,
        description=policy.description,
        start=policy.start,
        end=policy.end,
    )


async def policy_resolver(
    info: MOInfo,
    filter: PolicyFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = PolicyFilter()

    predicate = policy_predicate(info=info, filter=filter)
    query = select(db.Policy.id).where(predicate).order_by(db.Policy.id)
    session: AsyncSession = info.context.session
    uuids, next_cursor = await paginate(session, query, db.Policy.id, limit, cursor)

    result = await session.scalars(
        select(db.Policy).where(db.Policy.id.in_(uuids)).order_by(db.Policy.id)
    )
    return ObjectsAndCursor(
        objects=[_to_policy(policy) for policy in result],
        next_cursor=next_cursor,
    )


def actor_filter_for(
    uuid: UUID | None,
    username: str | None,
    roles: Collection[str],
) -> PolicyActorFilter:
    """Build the actor filter selecting policies applicable to an actor.

    Shared between the `me` collection (which seeds it from the calling client)
    and the permission-system instrumentation, so the notion of "which policies
    apply to whom" lives in one place.
    """
    return PolicyActorFilter(
        uuids=[uuid] if uuid is not None else None,
        usernames=[username] if username is not None else None,
        roles=list(roles) or None,
    )


async def actor_policies(info: MOInfo, token: Token) -> list[Policy]:
    """Return the currently-valid policies applicable to the given token's actor."""
    actor_filter = actor_filter_for(
        token.uuid, token.preferred_username, token.realm_access.roles
    )
    # Only currently-valid policies are relevant right now.
    current = now()
    predicate = policy_predicate(
        info, PolicyFilter(start=current, end=current, actor=actor_filter)
    )
    session: AsyncSession = info.context.session
    result = await session.scalars(select(db.Policy).where(predicate))
    return [_to_policy(policy) for policy in result]


async def actor_grants_field(
    info: MOInfo, token: Token, type: str, field: str
) -> bool:
    """Whether the calling actor may access the GraphQL ``(type, field)``.

    True if the actor has a currently-valid policy that applies to them (by
    uuid/username/role) and has a rule granting either ``(type, field)`` or
    ``(type, "*")``. This is the core of the PBAC permission engine.
    """
    actor_filter = actor_filter_for(
        token.uuid, token.preferred_username, token.realm_access.roles
    )
    current = now()
    rule_exists = (
        exists()
        .where(db.PolicyRule.policy_fk == db.Policy.id)
        .where(db.PolicyRule.type == type)
        .where(db.PolicyRule.field.in_([field, "*"]))
    )
    predicate = and_(
        policy_predicate(
            info, PolicyFilter(start=current, end=current, actor=actor_filter)
        ),
        rule_exists,
    )
    session: AsyncSession = info.context.session
    granted = await session.scalar(select(db.Policy.id).where(predicate).limit(1))
    return granted is not None
