# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rolebinding rules."""

from collections.abc import Sequence
from datetime import datetime
from textwrap import dedent
from typing import Any
from uuid import UUID

import psycopg
import strawberry
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import tuple_
from sqlalchemy.exc import IntegrityError

from mora import db
from mora.auth.middleware import get_authenticated_user
from mora.db import AsyncSession
from mora.db.events import add_event
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.rolebinding_rules.cel import RolebindingRuleCEL

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
    latest_versions = select(
        db.RolebindingRuleRevision.rule_fk,
        func.max(db.RolebindingRuleRevision.version),
    ).group_by(db.RolebindingRuleRevision.rule_fk)
    is_latest = tuple_(
        db.RolebindingRuleRevision.rule_fk, db.RolebindingRuleRevision.version
    ).in_(latest_versions)
    return is_latest & db.RolebindingRuleRevision.deleted.is_(False)


async def current_revision(
    session: AsyncSession, uuid: UUID
) -> db.RolebindingRuleRevision | None:
    """The current revision of a rule, or `None` if it is deleted or unknown."""
    return await session.scalar(
        select(db.RolebindingRuleRevision).where(
            db.RolebindingRuleRevision.rule_fk == uuid, _is_current()
        )
    )


async def add_revision(
    session: AsyncSession,
    rule: UUID,
    previous: db.RolebindingRuleRevision | None,
    **values: Any,
) -> None:
    """Writes a new revision of a rule, as the authenticated actor.

    The new revision follows *previous*, which must be the current revision of
    the rule, or `None` for a new rule.
    """
    try:
        await session.execute(
            insert(db.RolebindingRuleRevision).values(
                rule_fk=rule,
                version=previous.version + 1 if previous is not None else 1,
                actor=get_authenticated_user(),
                **values,
            )
        )
    except IntegrityError as error:
        assert isinstance(error.orig, psycopg.Error)
        if error.orig.diag.constraint_name == "rolebinding_rule_revision_version_key":
            raise ValueError(
                f"Rolebinding rule '{rule}' was changed concurrently. Try again."
            ) from error
        raise  # pragma: no cover


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

    def where_clauses(self: "RolebindingRuleFilter") -> list[ColumnElement[bool]]:
        """Clauses on the current revision of rules."""
        clauses: list[ColumnElement] = []
        if self.uuids is not None:
            clauses.append(db.RolebindingRuleRevision.rule_fk.in_(self.uuids))
        if self.names is not None:
            clauses.append(db.RolebindingRuleRevision.name.in_(self.names))
        if self.roles is not None:
            clauses.append(db.RolebindingRuleRevision.role.in_(self.roles))
        if self.active is not None:
            clauses.append(db.RolebindingRuleRevision.active == self.active)
        return clauses


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
        .where(db.RolebindingRule.pk.in_(uuids), _is_current())
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
        select(db.RolebindingRuleRevision.rule_fk)
        .where(_is_current(), *filter.where_clauses())
        .order_by(db.RolebindingRuleRevision.rule_fk)
    )
    uuids, next_cursor = await paginate(
        session, query, db.RolebindingRuleRevision.rule_fk, limit, cursor
    )
    return ObjectsAndCursor(
        objects=await load_rules(session, uuids),
        next_cursor=next_cursor,
    )
