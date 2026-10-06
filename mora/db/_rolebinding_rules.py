# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

import psycopg
from more_itertools import one
from sqlalchemy import BigInteger
from sqlalchemy import ColumnElement
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Identity
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import exists
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import aliased
from sqlalchemy.orm import mapped_column

from mora.cel.rolebinding_rules import RolebindingRuleCEL

from ._common import Base
from .events import add_event


class RolebindingRule(Base):
    """A rule granting a role to every IT-user matching a CEL expression.

    Rules are *not* bitemporal. A rule describes the desired state right now,
    and the engine reconciles the actual rolebindings with that state. However,
    we do keep a history for each rule. This table only holds the identity of a
    rule. The contents are in the revisions.
    """

    __tablename__ = "rolebinding_rule"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class RolebindingRuleRevision(Base):
    """One version of a rolebinding rule.

    Revisions of a rule are ordered by *version*. The highest is the newest.

    Deleting a rule writes a revision with `deleted` set. That revision copies
    the contents of the previous revision.
    """

    __tablename__ = "rolebinding_rule_revision"
    __table_args__ = (
        UniqueConstraint(
            "rule_fk", "version", name="rolebinding_rule_revision_version_key"
        ),
    )

    pk: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    rule_fk: Mapped[UUID] = mapped_column(ForeignKey("rolebinding_rule.pk"))
    version: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    actor: Mapped[UUID] = mapped_column(
        ForeignKey("actor.actor", name="rolebinding_rule_revision_actor_fkey")
    )
    deleted: Mapped[bool] = mapped_column(server_default=text("false"))

    name: Mapped[str]
    # The role (a class in the `role` facet) granted to matching IT-users.
    role: Mapped[UUID] = mapped_column(
        ForeignKey("klasse.id", name="rolebinding_rule_revision_role_fkey")
    )
    # The CEL expression matching the IT-users to grant the role to.
    expression: Mapped[RolebindingRuleCEL] = mapped_column(Text)
    active: Mapped[bool]

    @classmethod
    def is_current(cls) -> ColumnElement[bool]:
        """Whether the revision is the newest of a rule that is not deleted."""
        successor = aliased(cls)
        has_successor = exists().where(
            successor.rule_fk == cls.rule_fk,
            successor.version > cls.version,
        )
        return ~has_successor & cls.deleted.is_(False)


async def current_rolebinding_rule_revision(
    session: AsyncSession, uuid: UUID
) -> RolebindingRuleRevision | None:
    """The current revision of a rule, or `None` if it is deleted or unknown."""
    return await session.scalar(
        select(RolebindingRuleRevision).where(
            RolebindingRuleRevision.rule_fk == uuid,
            RolebindingRuleRevision.is_current(),
        )
    )


async def create_rolebinding_rule(
    session: AsyncSession,
    *,
    actor: UUID,
    name: str,
    role: UUID,
    expression: RolebindingRuleCEL,
    active: bool,
) -> UUID:
    """Create a rule with its first revision.

    Use `add_rolebinding_rule_revision` to change a rolebinding rule.
    """
    uuid = one(
        await session.scalars(insert(RolebindingRule).returning(RolebindingRule.pk))
    )
    await _insert_revision(
        session,
        rule=uuid,
        version=1,
        actor=actor,
        deleted=False,
        name=name,
        role=role,
        expression=expression,
        active=active,
    )
    return uuid


async def add_rolebinding_rule_revision(
    session: AsyncSession,
    previous: RolebindingRuleRevision,
    *,
    actor: UUID,
    name: str | None = None,
    role: UUID | None = None,
    expression: RolebindingRuleCEL | None = None,
    active: bool | None = None,
    deleted: bool = False,
) -> None:
    """Write a new revision of a rule.

    Fields left as `None` are copied from *previous*.
    """
    await _insert_revision(
        session,
        rule=previous.rule_fk,
        version=previous.version + 1,
        actor=actor,
        deleted=deleted,
        name=name if name is not None else previous.name,
        role=role if role is not None else previous.role,
        expression=expression if expression is not None else previous.expression,
        active=active if active is not None else previous.active,
    )


async def _insert_revision(
    session: AsyncSession,
    *,
    rule: UUID,
    version: int,
    actor: UUID,
    deleted: bool,
    name: str,
    role: UUID,
    expression: RolebindingRuleCEL,
    active: bool,
) -> None:
    try:
        await session.execute(
            insert(RolebindingRuleRevision).values(
                rule_fk=rule,
                version=version,
                actor=actor,
                deleted=deleted,
                name=name,
                role=role,
                expression=expression,
                active=active,
            )
        )
    except IntegrityError as error:
        assert isinstance(error.orig, psycopg.Error)
        if error.orig.diag.constraint_name == "rolebinding_rule_revision_version_key":
            raise ValueError(
                f"Rolebinding rule '{rule}' was changed concurrently. Try again."
            ) from error
        if error.orig.diag.constraint_name == "rolebinding_rule_revision_role_fkey":
            raise ValueError(f"Role '{role}' does not exist.") from error
        raise  # pragma: no cover

    await add_event(
        session, namespace="mo", routing_key="rolebinding_rule", subject=str(rule)
    )
