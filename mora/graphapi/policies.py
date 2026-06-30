# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
import json
from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING
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
from mora.graphapi.policy_cel import build_activation
from mora.graphapi.policy_cel import evaluate_condition
from mora.util import now

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate

if TYPE_CHECKING:  # pragma: no cover
    from mora.graphapi.filters import EmployeeFilter


@strawberry.enum(description="The kind of actor attribute a policy matches on.")
class PolicyActorKind(enum.Enum):
    uuid = "uuid"
    username = "username"
    role = "role"
    # Matches every actor regardless of attributes; the value is ignored.
    all = "all"
    # Matches every person the (serialized) `EmployeeFilter` in `value` resolves
    # to. Unlike the static kinds above this is evaluated dynamically: a policy
    # applies to an actor if the actor's uuid is among the persons the filter
    # matches (see `_person_filter_policy_ids`).
    person_filter = "person_filter"


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
    if criteria:
        # An "all" actor matches every actor, so a policy with one satisfies any
        # attribute-based actor filter.
        criteria.append(db.PolicyActor.kind == PolicyActorKind.all.value)
        inner = or_(*criteria)
    else:
        # No attributes provided (`{}`) means "has any actor" (existence only),
        # which already includes "all" actors.
        inner = true()
    return exists().where(db.PolicyActor.policy_fk == db.Policy.id).where(inner)


def deserialize_person_filter(value: str) -> "EmployeeFilter":
    """Deserialize a stored `person_filter` actor value into an `EmployeeFilter`.

    The value is the JSON serialization of an `EmployeeFilter` input (the shape
    the GraphQL API accepts). Raises `ValueError` if the value is not valid JSON
    or does not describe a well-formed filter, so callers can reject it at
    declare time and skip it at evaluation time.
    """
    # Imported lazily: this module is imported by inputs/mutators, while the
    # filters module pulls in the wider GraphQL layer.
    from strawberry import UNSET

    from mora.graphapi.filters import EmployeeFilter
    from mora.graphapi.filters import EmployeeRegistrationFilter
    from mora.util import CPR

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"person_filter value is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("person_filter value must be a JSON object")

    def dt(key: str) -> datetime | None:
        raw = data.get(key)
        return datetime.fromisoformat(raw) if raw is not None else None

    # `from_date`, `to_date` and `query` default to UNSET (not None) on
    # `EmployeeFilter`; preserve that distinction so an absent key behaves like
    # a normal query rather than forcing an explicit null.
    def absent_or_dt(key: str) -> datetime | None:
        return dt(key) if key in data else UNSET

    try:
        registration = None
        reg = data.get("registration")
        if reg is not None:
            registration = EmployeeRegistrationFilter(
                actors=(
                    [UUID(a) for a in reg["actors"]]
                    if reg.get("actors") is not None
                    else None
                ),
                start=(
                    datetime.fromisoformat(reg["start"])
                    if reg.get("start") is not None
                    else None
                ),
                end=(
                    datetime.fromisoformat(reg["end"])
                    if reg.get("end") is not None
                    else None
                ),
            )

        return EmployeeFilter(
            uuids=(
                [UUID(u) for u in data["uuids"]]
                if data.get("uuids") is not None
                else None
            ),
            user_keys=data.get("user_keys"),
            from_date=absent_or_dt("from_date"),
            to_date=absent_or_dt("to_date"),
            registration_time=dt("registration_time"),
            registration=registration,
            query=data.get("query", UNSET),
            cpr_numbers=(
                [CPR(c) for c in data["cpr_numbers"]]
                if data.get("cpr_numbers") is not None
                else None
            ),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"malformed person_filter: {exc}") from exc


async def _person_filter_policy_ids(info: MOInfo, uuids: Collection[UUID]) -> set[UUID]:
    """Policies that have a `person_filter` actor matching any of `uuids`.

    Each `person_filter` actor stores a distinct, dynamic `EmployeeFilter`, so
    it cannot be expressed as a single static SQL predicate. We evaluate each
    one with the shared employee predicate, asking "is any of `uuids` among the
    persons this filter matches?".
    """
    if not uuids:
        return set()

    # Lazy import: `resolvers` belongs to the wider GraphQL layer that imports
    # this module transitively.
    from mora.graphapi.resolvers import employee_predicate

    session: AsyncSession = info.context.session
    rows = await session.execute(
        select(db.PolicyActor.policy_fk, db.PolicyActor.value).where(
            db.PolicyActor.kind == PolicyActorKind.person_filter.value
        )
    )
    matched: set[UUID] = set()
    for policy_fk, value in rows:
        if policy_fk in matched:
            continue
        try:
            person_filter = deserialize_person_filter(value)
        except ValueError:
            # A malformed stored filter matches nothing rather than erroring the
            # whole request.
            continue
        predicate = and_(
            employee_predicate(info, person_filter),
            db.BrugerRegistrering.bruger_id.in_(uuids),
        )
        if await session.scalar(select(exists().where(predicate))):
            matched.add(policy_fk)
    return matched


def policy_predicate(
    info: MOInfo,
    filter: PolicyFilter,
    person_filter_policy_ids: Collection[UUID] = (),
) -> ColumnElement:
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
        actor_predicate = _policy_actor_predicate(filter.actor)
        # `person_filter` actors are matched dynamically (out of band, see
        # `_person_filter_policy_ids`); a policy in that precomputed set also
        # satisfies the actor filter.
        if person_filter_policy_ids:
            actor_predicate = or_(
                actor_predicate, db.Policy.id.in_(person_filter_policy_ids)
            )
        predicates.append(actor_predicate)

    return and_(*predicates)


async def policy_predicate_async(info: MOInfo, filter: PolicyFilter) -> ColumnElement:
    """`policy_predicate` augmented with dynamic `person_filter` actor matching.

    Use this instead of `policy_predicate` whenever the actor filter should also
    match `person_filter` actors (i.e. when filtering by actor uuid).
    """
    person_filter_policy_ids: set[UUID] = set()
    if filter.actor is not None and filter.actor.uuids:
        person_filter_policy_ids = await _person_filter_policy_ids(
            info, filter.actor.uuids
        )
    return policy_predicate(info, filter, person_filter_policy_ids)


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
    condition: str | None = strawberry.field(
        description=(
            "Optional CEL condition that must evaluate true for the rule to "
            "grant access. Null means the rule is unconditional."
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
            PolicyRule(
                uuid=rule.pk,
                type=rule.type,
                field=rule.field,
                condition=rule.condition,
            )
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

    predicate = await policy_predicate_async(info=info, filter=filter)
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
    predicate = await policy_predicate_async(
        info, PolicyFilter(start=current, end=current, actor=actor_filter)
    )
    session: AsyncSession = info.context.session
    result = await session.scalars(select(db.Policy).where(predicate))
    return [_to_policy(policy) for policy in result]


async def actor_grants_field(
    info: MOInfo,
    token: Token,
    type: str,
    field: str,
    permission: str | None = None,
) -> bool:
    """Whether the calling actor may access the GraphQL ``(type, field)``.

    True if the actor has a currently-valid policy that applies to them (by
    uuid/username/role) and has a rule granting either ``(type, field)`` or
    ``(type, "*")`` whose CEL condition (if any) holds. This is the core of the
    PBAC permission engine.

    ``permission`` is the role the field requires under legacy RBAC; it is
    exposed to conditions (e.g. ``permission in token.roles``).

    SQL narrows the work to the candidate rules' conditions (a tiny set), then
    any conditions are evaluated in Python/CEL: an unconditional rule grants
    outright, otherwise access is granted if any condition evaluates true.
    """
    actor_filter = actor_filter_for(
        token.uuid, token.preferred_username, token.realm_access.roles
    )
    current = now()
    predicate = await policy_predicate_async(
        info, PolicyFilter(start=current, end=current, actor=actor_filter)
    )
    query = (
        select(db.PolicyRule.condition)
        .where(db.PolicyRule.policy_fk == db.Policy.id)
        .where(predicate)
        .where(db.PolicyRule.type == type)
        .where(db.PolicyRule.field.in_([field, "*"]))
    )
    session: AsyncSession = info.context.session
    conditions = (await session.scalars(query)).all()
    if not conditions:
        return False
    # An unconditional matching rule grants access outright.
    if any(condition is None for condition in conditions):
        return True
    # Otherwise the actor is granted access if any condition holds. The
    # activation (the variable context) is built once and reused across every
    # candidate condition.
    activation = build_activation(token, permission)
    return any(
        evaluate_condition(condition, activation) for condition in conditions
    )
