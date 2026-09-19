# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The tables holding access control as data."""

from uuid import UUID

from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ._collections import Collection
from ._common import Base


class Policy(Base):
    """Policies assign meaning to roles."""

    __tablename__ = "policy"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(Text, unique=True)
    description: Mapped[str] = mapped_column(Text, server_default="")
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    role: Mapped[str] = mapped_column(Text, index=True)

    read_rules: Mapped[list["PolicyReadRule"]] = relationship(back_populates="policy")


class PolicyReadRule(Base):
    """Grants read access on a collection to a policy."""

    __tablename__ = "policy_read_rule"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    collection: Mapped[Collection] = mapped_column(
        Enum(Collection, name="policycollection")
    )
    condition: Mapped[str] = mapped_column(Text, server_default="")
    graphql_version: Mapped[int] = mapped_column(Integer)
    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.pk"))
    policy: Mapped[Policy] = relationship(back_populates="read_rules")

    fields: Mapped[list["PolicyReadRuleField"]] = relationship(back_populates="rule")


class PolicyReadRuleField(Base):
    """Grants read access to a field of that collection."""

    __tablename__ = "policy_read_rule_field"

    rule_fk: Mapped[UUID] = mapped_column(
        ForeignKey("policy_read_rule.pk"), primary_key=True
    )
    field: Mapped[str] = mapped_column(Text, primary_key=True)
    rule: Mapped[PolicyReadRule] = relationship(back_populates="fields")
