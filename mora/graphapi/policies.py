# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from collections.abc import Collection

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


@strawberry.enum(description="The kind of actor attribute a policy matches on.")
class PolicyActorKind(enum.Enum):
    # Matches an actor carrying this Keycloak token role/claim.
    role = "role"
    # Matches every actor regardless of attributes; the value is ignored.
    all = "all"


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
    activated: bool | None = strawberry.field(
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
                db.PolicyActor.kind == PolicyActorKind.role.value,
                db.PolicyActor.value.in_(filter.roles),
            )
        )
    if criteria:
        # An "all" actor matches every actor, so a policy with one satisfies any
        # role-based actor filter.
        criteria.append(db.PolicyActor.kind == PolicyActorKind.all.value)
        inner = or_(*criteria)
    else:
        # No roles provided (`{}`) means "has any actor" (existence only), which
        # already includes "all" actors.
        inner = true()
    return exists().where(db.PolicyActor.policy_fk == db.Policy.id).where(inner)


def policy_predicate(filter: PolicyFilter) -> ColumnElement:
    predicates: list[ColumnElement] = [true()]

    if filter.activated is not None:
        predicates.append(db.Policy.activated == filter.activated)

    if filter.actor is not None:
        predicates.append(_policy_actor_predicate(filter.actor))

    return and_(*predicates)


def actor_filter_for(roles: Collection[str]) -> PolicyActorFilter:
    """Build the actor filter selecting policies applicable to an actor.

    The roles are passed as a concrete list (empty when the actor has none) so a
    roleless actor still matches `all` actors but nothing else -- as opposed to
    a null `roles`, which is the "match any actor" existence filter.
    """
    return PolicyActorFilter(roles=list(roles))


async def _applicable_rule_index(
    info: MOInfo, token: Token
) -> dict[tuple[str, str], list[str | None]]:
    """The rules of the caller's active policies, cached per request.

    Every field resolve consults the policy engine, so the applicable rules --
    the rules of the active policies whose actor matches the caller -- are
    fetched once and cached on the request context, keyed by their
    ``(type, field)`` for O(1) candidate lookup. The caller (roles) is constant
    within a request, so the set is too; this turns a query that resolves many
    fields into a single policy query.
    """
    context = info.context
    if context.applicable_policy_rules is None:
        actor_filter = actor_filter_for(token.realm_access.roles)
        predicate = policy_predicate(PolicyFilter(activated=True, actor=actor_filter))
        query = (
            select(
                db.PolicyRule.type,
                db.PolicyRule.field,
                db.PolicyRule.condition,
            )
            .where(db.PolicyRule.policy_fk == db.Policy.id)
            .where(predicate)
        )
        session: AsyncSession = context.session
        index: dict[tuple[str, str], list[str | None]] = {}
        for rule_type, rule_field, condition in (await session.execute(query)).all():
            index.setdefault((rule_type, rule_field), []).append(condition)
        context.applicable_policy_rules = index
    return context.applicable_policy_rules


async def actor_grants_field(
    info: MOInfo,
    token: Token,
    type: str,
    field: str,
) -> bool:
    """Whether the calling actor may access the GraphQL ``(type, field)``.

    True if the actor has an active policy that applies to them (by role) and
    has a rule granting the ``(type, field)`` -- where either component may be
    the wildcard ``"*"`` -- whose CEL condition (if any) holds. This is the
    core of the policy-based access control (PBAC) permission engine.

    The applicable rules are fetched once per request (see
    :func:`_applicable_rule_index`); the candidates for this ``(type, field)``
    are then checked in Python: a rule grants when its condition (if any)
    holds; a rule without one grants outright.
    """
    index = await _applicable_rule_index(info, token)
    # Candidate rules match this exact (type, field) or a wildcard in either
    # component (``type IN (type,'*') AND field IN (field,'*')``).
    rules = (
        index.get((type, field), [])
        + index.get((type, "*"), [])
        + index.get(("*", field), [])
        + index.get(("*", "*"), [])
    )
    if not rules:
        return False
    # Access is granted if any candidate rule is satisfied. The condition
    # activation is built once and reused across rules.
    activation = None
    for condition in rules:
        if condition is not None:
            if activation is None:
                activation = build_activation(token)
            if not evaluate_condition(condition, activation):
                continue
        return True
    return False
