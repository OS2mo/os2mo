# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The policy tables.

A policy names the actors it applies to with its selectors, and grants them the
fields its readers name and the mutators its mutators name.
"""

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy import CheckConstraint
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import false
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ._common import Base


class PolicySelectorKind(enum.Enum):
    """The kind of principal attribute a selector matches on."""

    # Matches an actor based on their Keycloak roles; `value` is the role
    role = "role"
    # Matches every actor; `value` is ignored
    all = "all"


class Policy(Base):
    __tablename__ = "policy"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text, server_default="")
    # Whether the policy is in effect. A policy only grants access while active
    active: Mapped[bool] = mapped_column(server_default=false())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    selectors: Mapped[list["PolicySelector"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    readers: Mapped[list["PolicyReader"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    mutators: Mapped[list["PolicyMutator"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


class PolicySelector(Base):
    __tablename__ = "policy_selector"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The kind of principal + kind-specific value to match on
    kind: Mapped[PolicySelectorKind] = mapped_column(
        Enum(PolicySelectorKind, name="policy_selector_kind")
    )
    value: Mapped[str] = mapped_column(Text, server_default="")

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="selectors")

    __table_args__ = (
        # value must be non-empty if kind is anything but "all"
        CheckConstraint("kind = 'all' OR value <> ''", name="ck_policy_selector_value"),
        # A given (kind, value) is declared at most once per policy
        UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_selector"),
    )


class PolicyReader(Base):
    __tablename__ = "policy_reader"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The collection whose objects the rule reads
    collection: Mapped[str] = mapped_column(Text)
    # The readable fields on the collection's type
    fields: Mapped[list[str]] = mapped_column(JSON, server_default="[]")
    # CEL condition the caller must pass for the rule to apply; "" always holds
    condition: Mapped[str] = mapped_column(Text, server_default="")
    # CEL filter naming the objects the rule reaches; "" reaches every object
    filter: Mapped[str] = mapped_column(Text, server_default="")

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="readers")

    __table_args__ = (
        UniqueConstraint("policy_fk", "collection", "filter", name="uq_policy_reader"),
    )


class PolicyMutator(Base):
    """A policy names a mutator once per way of owning what it changes."""

    __tablename__ = "policy_mutator"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The GraphQL mutation field the mutator names
    name: Mapped[str] = mapped_column(Text)
    # CEL condition the call must pass for the rule to apply; "" always holds
    condition: Mapped[str] = mapped_column(Text, server_default="")
    # CEL filter naming what the caller must own, as `{collection, filter}`
    # specs; "" requires nothing owned, and naming nothing owns nothing
    filter: Mapped[str] = mapped_column(Text, server_default="")

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="mutators")
