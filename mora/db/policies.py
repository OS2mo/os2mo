# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ._common import Base


class Policy(Base):
    __tablename__ = "policy"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str]
    description: Mapped[str | None]
    # Whether the policy is in effect. A policy only grants access while active.
    activated: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    actors: Mapped[list["PolicyActor"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    rules: Mapped[list["PolicyRule"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


class PolicyActor(Base):
    __tablename__ = "policy_actor"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The kind of actor to match on: "role" (a Keycloak token role/claim) or
    # "all" (every actor).
    kind: Mapped[str]
    # The value the attribute must equal: a role name, or empty for "all".
    value: Mapped[str]

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="actors")

    # A given (kind, value) is declared at most once per policy.
    __table_args__ = (
        UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_actor"),
    )


class PolicyRule(Base):
    __tablename__ = "policy_rule"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The resource a rule grants access to, expressed GraphQL-natively as a
    # (type, field) pair: `type` is a GraphQL type (a collection's object type,
    # or "Query"/"Mutation") and `field` is a field/mutator on it, or "*" for
    # all fields.
    type: Mapped[str]
    field: Mapped[str]
    # Optional CEL (Common Expression Language) condition gating the grant: the
    # rule only applies when this boolean expression evaluates true against the
    # request context (see mora/graphapi/policy_cel.py). A null condition is
    # unconditional. The same (type, field) may carry several conditions, each a
    # separate rule, granting access if any of them holds.
    condition: Mapped[str | None]

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="rules")

    # A given (type, field, condition) is declared at most once per policy.
    # NULLs are treated as equal so an unconditional rule is also deduplicated
    # (requires PostgreSQL >= 15).
    __table_args__ = (
        UniqueConstraint(
            "policy_fk",
            "type",
            "field",
            "condition",
            name="uq_policy_rule",
            postgresql_nulls_not_distinct=True,
        ),
    )
