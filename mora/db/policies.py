# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ._common import Base


class PolicyActorKind(enum.Enum):
    """The kind of actor attribute a policy matches on."""

    # Matches an actor based on their Keycloak roles / claim
    # Value must be set to the role to check for
    role = "role"

    # Matches every actor
    # Value is ignored for this kind
    all = "all"


class Policy(Base):
    __tablename__ = "policy"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.uuid_generate_v4()
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, server_default="")
    # Whether the policy is in effect. A policy only grants access while active
    active: Mapped[bool] = mapped_column(server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    actors: Mapped[list["PolicyActor"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    rules: Mapped[list["PolicyRule"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


class PolicyActor(Base):
    __tablename__ = "policy_actor"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.uuid_generate_v4()
    )
    # The kind of actor + kind-specific value to match on (see PolicyActorKind)
    kind: Mapped[PolicyActorKind] = mapped_column(
        Enum(PolicyActorKind, name="policy_actor_kind")
    )
    value: Mapped[str] = mapped_column(Text, server_default="")

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="actors")

    __table_args__ = (
        # value must be non-empty if kind is anything but "all"
        CheckConstraint("kind = 'all' OR value <> ''", name="ck_policy_actor_value"),
        # A given (kind, value) is declared at most once per policy
        UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_actor"),
    )


class PolicyRule(Base):
    __tablename__ = "policy_rule"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.uuid_generate_v4()
    )
    # The GraphQL (type, field) the rule grants access to; either may be "*"
    type: Mapped[str] = mapped_column(Text)
    field: Mapped[str] = mapped_column(Text)
    # Optional CEL condition that must hold for the rule to apply
    condition: Mapped[str] = mapped_column(Text, server_default="")

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="rules")

    __table_args__ = (
        # A given (type, field, condition) is declared at most once per policy.
        UniqueConstraint(
            "policy_fk", "type", "field", "condition", name="uq_policy_rule"
        ),
    )
