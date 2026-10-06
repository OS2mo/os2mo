# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rolebinding rules."""

from collections.abc import Sequence
from datetime import datetime
from textwrap import dedent
from typing import Any
from typing import NewType
from uuid import UUID

import strawberry
from more_itertools import bucket
from more_itertools import last
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import aliased

from mora import db
from mora.auth.middleware import get_authenticated_user
from mora.db import AsyncSession
from mora.db.events import add_event
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.rolebinding_rules.cel import validate

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

    | Field                                    | Type                   | Holds                                                     |
    |------------------------------------------|------------------------|-----------------------------------------------------------|
    | `ituser.person`                          | object or `null`       | The person owning the IT-user, or `null` if no person owns the IT-user. |
    | `ituser.person.uuid`                     | `string`               | UUID of the person.                                       |
    | `ituser.engagement`                      | object or `null`       | The engagement linked to the IT-user, or `null` if no engagement is linked. |
    | `ituser.engagement.job_function.uuid`    | `string`               | UUID of the engagement's job function.                    |
    | `ituser.engagement.engagement_type.uuid` | `string`               | UUID of the engagement's engagement type.                 |
    | `ituser.engagement.org_unit.uuid`        | `string`               | UUID of the engagement's organisation unit.               |
    | `ituser.engagement.org_unit.path_uuids`  | `list(string)`         | UUIDs of the engagement's organisation unit and of every unit above it. |

    To match an organisation unit and every unit below it, use the `in`
    operator on `path_uuids`. To match only the unit itself, compare the
    unit's UUID with `org_unit.uuid`.

    `ituser.person` and `ituser.engagement` can hold `null`. Reading a field of
    `null`, such as `ituser.engagement.org_unit` for an IT-user without an
    engagement, is an error in CEL. You should add a guard before reading a
    field:

    * Before reading the engagement, write `ituser.engagement != null &&`.
    * Before reading the person, write `ituser.person != null &&`.

    Do not use `has(ituser.engagement)` or `has(ituser.person)` as a null
    check. Both fields always exist.
    """
)


async def notify_rule_changed(session: AsyncSession, uuid: UUID) -> None:
    """Send events in the event system."""
    await add_event(
        session,
        namespace="mo",
        routing_key="rolebinding_rule",
        subject=str(uuid),
    )


def _is_current() -> ColumnElement[bool]:
    """Restricts revisions to the current revision of rules that are not deleted."""
    revision = aliased(db.RolebindingRuleRevision)
    latest = select(func.max(revision.pk)).group_by(revision.rule_fk)
    return db.RolebindingRuleRevision.pk.in_(latest) & (
        db.RolebindingRuleRevision.deleted.is_(False)
    )


async def current_revision(
    session: AsyncSession, uuid: UUID
) -> db.RolebindingRuleRevision | None:
    """The current revision of a rule, or `None` if it is deleted or unknown."""
    revision = await session.scalar(
        select(db.RolebindingRuleRevision)
        .where(db.RolebindingRuleRevision.rule_fk == uuid)
        .order_by(db.RolebindingRuleRevision.pk.desc())
        .limit(1)
    )
    if revision is None or revision.deleted:
        return None
    return revision


async def add_revision(session: AsyncSession, rule: UUID, **values: Any) -> None:
    """Writes a new revision of a rule, as the authenticated actor."""
    await session.execute(
        insert(db.RolebindingRuleRevision).values(
            rule_fk=rule, actor=get_authenticated_user(), **values
        )
    )


@strawberry.input(description="Rolebinding rule filter.")
class RolebindingRuleFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    user_keys: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("User-key", "user_keys")
    )
    roles: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Role UUID", "roles")
    )
    active: bool | None = strawberry.field(
        default=None,
        description="Only return rules with this activation status.",
    )
    deleted: bool | None = strawberry.field(
        default=None,
        description="To be, or not to be.",
    )

    def where_clauses(self: "RolebindingRuleFilter") -> list[ColumnElement[bool]]:
        clauses: list[ColumnElement] = []

        if self.uuids is not None:
            clauses.append(db.RolebindingRule.pk.in_(self.uuids))

        current: list[ColumnElement] = []
        if self.user_keys is not None:
            current.append(db.RolebindingRuleRevision.user_key.in_(self.user_keys))
        if self.roles is not None:
            current.append(db.RolebindingRuleRevision.role.in_(self.roles))
        if self.active is not None:
            current.append(db.RolebindingRuleRevision.active == self.active)
        if current:
            clauses.append(
                db.RolebindingRule.pk.in_(
                    select(db.RolebindingRuleRevision.rule_fk).where(
                        _is_current(), *current
                    )
                )
            )

        if self.deleted is not None:
            not_deleted = db.RolebindingRule.pk.in_(
                select(db.RolebindingRuleRevision.rule_fk).where(_is_current())
            )
            clauses.append(~not_deleted if self.deleted else not_deleted)

        return clauses


# A CEL expression the rolebinding rule engine can run
RolebindingRuleCEL = NewType("RolebindingRuleCEL", str)


def _parse_rule_expression(expression: str) -> RolebindingRuleCEL:
    validate(expression)
    return RolebindingRuleCEL(expression)


ROLEBINDING_RULE_CEL_SCALAR = strawberry.scalar(
    name="RolebindingRuleCEL",
    serialize=str,
    parse_value=_parse_rule_expression,
    description="A CEL expression used in rolebinding rules.",
)


@strawberry.type(
    description=dedent(
        """\
        One version of a rolebinding rule.

        Revisions are never changed once written. Changing a rule writes a new
        revision, which becomes the current one.
        """
    )
)
class RolebindingRuleRevision:
    created_at: datetime = strawberry.field(
        description="When the revision was written."
    )
    actor_uuid: strawberry.Private[UUID]

    @strawberry.field(description="The integration or user who wrote the revision.")
    def actor(self) -> LazyActor:
        from .actor import actor_uuid_to_actor

        return actor_uuid_to_actor(self.actor_uuid)

    deleted: bool = strawberry.field(
        description=dedent(
            """\
            Whether this revision deleted the rule.

            A deleting revision copies the contents of the previous revision.
            """
        )
    )
    user_key: str = strawberry.field(
        description="Human-readable identifier of the rule.",
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
        description=dedent(
            """\
            The role (class) granted by the rule.

            The rule grants rolebindings in the IT-system of the role.
            """
        ),
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
    history: list[RolebindingRuleRevision] = strawberry.field(
        description=dedent(
            """\
            Every revision of the rule, oldest first.

            Includes the revision deleting the rule, if it is deleted.
            """
        )
    )

    @strawberry.field(
        description="The current revision of the rule. `null` if the rule is deleted."
    )
    def current(self) -> RolebindingRuleRevision | None:
        revision = last(self.history)
        return None if revision.deleted else revision


def db_to_revision(revision: db.RolebindingRuleRevision) -> RolebindingRuleRevision:
    return RolebindingRuleRevision(  # type: ignore[call-arg]
        created_at=revision.created_at,
        actor_uuid=revision.actor,
        deleted=revision.deleted,
        user_key=revision.user_key,
        expression=RolebindingRuleCEL(revision.expression),
        active=revision.active,
        role_uuid=revision.role,
    )


async def load_rules(
    session: AsyncSession, uuids: Sequence[UUID]
) -> list[RolebindingRule]:
    """The rules with the given UUIDs, ordered by UUID."""
    rules = await session.scalars(
        select(db.RolebindingRule)
        .where(db.RolebindingRule.pk.in_(uuids))
        .order_by(db.RolebindingRule.pk)
    )
    revisions = bucket(
        (
            await session.scalars(
                select(db.RolebindingRuleRevision)
                .where(db.RolebindingRuleRevision.rule_fk.in_(uuids))
                .order_by(db.RolebindingRuleRevision.pk)
            )
        ).all(),
        key=lambda revision: revision.rule_fk,
    )
    return [
        RolebindingRule(  # type: ignore[call-arg]
            uuid=rule.pk,
            created_at=rule.created_at,
            history=[db_to_revision(revision) for revision in revisions[rule.pk]],
        )
        for rule in rules
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
        .where(*filter.where_clauses())
        .order_by(db.RolebindingRule.pk)
    )
    uuids, next_cursor = await paginate(
        session, query, db.RolebindingRule.pk, limit, cursor
    )
    return ObjectsAndCursor(
        objects=await load_rules(session, uuids),
        next_cursor=next_cursor,
    )
