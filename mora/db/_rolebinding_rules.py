# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import Identity
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import Base


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
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class RolebindingRuleRevision(Base):
    """One version of a rolebinding rule.

    Deleting a rule writes a revision with `deleted` set. That revision copies
    the contents of the previous revision.

    The latest revision is the current one.
    """

    __tablename__ = "rolebinding_rule_revision"

    pk: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    rule_fk: Mapped[UUID] = mapped_column(ForeignKey("rolebinding_rule.pk"))

    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    actor: Mapped[UUID]
    deleted: Mapped[bool] = mapped_column(server_default=text("false"))

    user_key: Mapped[str]
    # The role (a class in the `role` facet) granted to matching IT-users.
    role: Mapped[UUID]
    # The CEL expression matching the IT-users to grant the role to.
    expression: Mapped[str]
    active: Mapped[bool]
