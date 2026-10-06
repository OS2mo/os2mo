# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rolebinding rules."""

from collections.abc import Sequence
from datetime import datetime
from textwrap import dedent
from uuid import UUID

import strawberry
from sqlalchemy import ColumnElement
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import true

from mora import db
from mora.cel.rolebinding_rules import RolebindingRuleCEL
from mora.config import Settings
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo
from mora.graphapi.custom_schema import get_version
from mora.graphapi.filters import gen_filter_string
from mora.graphapi.version import Version

from .actor import actor_uuid_to_actor
from .lazy import LazyActor
from .lazy import LazyClass
from .models import ClassRead
from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate
from .response import Response

CEL_EXPRESSION_DESCRIPTION = dedent(
    """\
    A Common Expression Language (CEL) expression that decides which IT-users
    get the rule's role. The expression must evaluate to `true` or `false`.

    For the full language, see https://cel.dev.

    CEL has no UUID type. Write UUIDs as lowercase strings in double quotes.

    The following fields are available in the environment that expressions are
    evaluated:

    | Field                 | Type               | Holds                                                     |
    |-----------------------|--------------------|-----------------------------------------------------------|
    | `ituser.uuid`         | `string`           | UUID of the IT-user.                                      |
    | `ituser.user_key`     | `string`           | User key of the IT-user, e.g. the username.               |
    | `ituser.external_id`  | `string`           | ID of the IT-user in the external IT-system.              |
    | `ituser.engagements`  | `list(Engagement)` | The engagements linked to the IT-user. Empty if none are linked. |

    Each engagement has the following fields:

    | Field                  | Type           | Holds                                                     |
    |------------------------|----------------|-----------------------------------------------------------|
    | `uuid`                 | `string`       | UUID of the engagement.                                   |
    | `job_function.uuid`    | `string`       | UUID of the engagement's job function.                    |
    | `engagement_type.uuid` | `string`       | UUID of the engagement's engagement type.                 |
    | `org_unit.uuid`        | `string`       | UUID of the engagement's organisation unit.               |
    | `org_unit.path_uuids`  | `list(string)` | UUIDs of the engagement's organisation unit and of every unit above it. |

    Use `exists` to match IT-users with at least one engagement fulfilling a
    condition, e.g. `ituser.engagements.exists(e, e.job_function.uuid == "...")`.
    Use `all` to require it of every engagement. `exists` is `false` and `all`
    is `true` for an IT-user without engagements. To match IT-users without
    engagements, write `size(ituser.engagements) == 0`.

    Conditions within one `exists` must hold for the same engagement. Conditions
    in separate `exists` may hold for different engagements.

    To match an organisation unit and every unit below it, use the `in`
    operator on `path_uuids`, e.g.
    `ituser.engagements.exists(e, "..." in e.org_unit.path_uuids)`. To match
    only the unit itself, compare the unit's UUID with `org_unit.uuid`.
    """
)


@strawberry.input(description="Rolebinding rule filter.")
class RolebindingRuleFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    names: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Name", "names")
    )
    roles: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Role UUID", "roles")
    )
    active: bool | None = strawberry.field(
        default=None,
        description="Only return rules with this activation status.",
    )


def rolebinding_rule_revision_predicate(
    settings: Settings, version: Version, filter: RolebindingRuleFilter
) -> ColumnElement[bool]:
    """The clause holding where a revision matches the filter."""
    clauses: list[ColumnElement] = []

    if filter.uuids is not None:
        clauses.append(db.RolebindingRuleRevision.rule_fk.in_(filter.uuids))

    if filter.names is not None:
        clauses.append(db.RolebindingRuleRevision.name.in_(filter.names))

    if filter.roles is not None:
        clauses.append(db.RolebindingRuleRevision.role.in_(filter.roles))

    if filter.active is not None:
        clauses.append(db.RolebindingRuleRevision.active == filter.active)

    return and_(true(), *clauses)


def rolebinding_rule_predicate(
    settings: Settings, version: Version, filter: RolebindingRuleFilter
) -> ColumnElement[bool]:
    """The clause holding where a rule's current revision matches the filter."""
    return db.RolebindingRule.pk.in_(
        select(db.RolebindingRuleRevision.rule_fk).where(
            db.RolebindingRuleRevision.is_current(),
            rolebinding_rule_revision_predicate(settings, version, filter),
        )
    )


@strawberry.type(description="One version of a rolebinding rule.")
class RolebindingRuleRevision:
    pk: strawberry.Private[int]
    created_at: datetime = strawberry.field(
        description="When the revision was written."
    )
    actor_uuid: strawberry.Private[UUID]

    @strawberry.field(description="The integration or user who wrote the revision.")
    def actor(self) -> LazyActor:
        return actor_uuid_to_actor(self.actor_uuid)

    name: str = strawberry.field(
        description="Human-readable name of the rule.",
    )
    expression: RolebindingRuleCEL = strawberry.field(
        description=CEL_EXPRESSION_DESCRIPTION,
    )
    active: bool = strawberry.field(
        description="Whether the engine should act on this rule.",
    )
    role_uuid: strawberry.Private[UUID]

    role: Response[LazyClass] = strawberry.field(  # type: ignore[assignment]
        resolver=lambda root: Response(model=ClassRead, uuid=root.role_uuid),
        description="The role granted by the rule.",
    )


@strawberry.type(
    description=dedent(
        """\
        A rule granting a rolebinding to every IT-user matching a CEL expression.

        The rolebinding engine reconciles the rolebindings asynchronously, so
        they do not exist yet when a mutation returns.
        """
    )
)
class RolebindingRule:
    uuid: UUID = strawberry.field(description="ID of the rule.")
    created_at: datetime = strawberry.field(description="When the rule was created.")
    current: RolebindingRuleRevision = strawberry.field(
        description="The current revision of the rule."
    )


def db_to_revision(revision: db.RolebindingRuleRevision) -> RolebindingRuleRevision:
    return RolebindingRuleRevision(  # type: ignore[call-arg]
        pk=revision.pk,
        created_at=revision.created_at,
        actor_uuid=revision.actor,
        name=revision.name,
        expression=revision.expression,
        active=revision.active,
        role_uuid=revision.role,
    )


async def load_rules(
    session: AsyncSession, uuids: Sequence[UUID]
) -> list[RolebindingRule]:
    rows = await session.execute(
        select(db.RolebindingRule, db.RolebindingRuleRevision)
        .join(
            db.RolebindingRuleRevision,
            db.RolebindingRuleRevision.rule_fk == db.RolebindingRule.pk,
        )
        .where(
            db.RolebindingRule.pk.in_(uuids), db.RolebindingRuleRevision.is_current()
        )
        .order_by(db.RolebindingRule.pk)
    )
    return [
        RolebindingRule(
            uuid=rule.pk,
            created_at=rule.created_at,
            current=db_to_revision(revision),
        )
        for rule, revision in rows.tuples()
    ]


async def rolebinding_rule_resolver(
    info: MOInfo,
    filter: RolebindingRuleFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = RolebindingRuleFilter()

    session: AsyncSession = info.context.session

    query = (
        select(db.RolebindingRule.pk)
        .where(
            rolebinding_rule_predicate(
                info.context.settings, get_version(info.schema), filter
            )
        )
        .order_by(db.RolebindingRule.pk)
    )
    uuids, next_cursor = await paginate(
        session, query, db.RolebindingRule.pk, limit, cursor
    )
    return ObjectsAndCursor(
        objects=await load_rules(session, uuids),
        next_cursor=next_cursor,
    )
