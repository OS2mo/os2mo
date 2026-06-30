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

# Well-known "magic" UUID of the bootstrap "policyadmin" policy. It is inserted
# by a migration and protected from deletion via the `policy_delete` mutator.
POLICYADMIN_UUID = UUID("ded1ca7e-9bac-5eed-706f-6c61646d696e")


class Policy(Base):
    __tablename__ = "policy"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str]
    description: Mapped[str | None]
    # Validity is modelled as two plain timestamps. A null `end` means the policy
    # is open-ended. This is not bitemporal like the LoRa entities.
    start: Mapped[datetime]
    end: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    actors: Mapped[list["PolicyActor"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    rules: Mapped[list["PolicyRule"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


# TODO: Support applying a policy to all employees matching a dynamic MO
# filter, not just the static (kind, value) attributes below. For example,
# assign a policy to all managers under a specific organisation unit, or to all
# employees with an engagement in a given organisation unit.
#
# The idea: add an actor `kind` (e.g. "employee_filter") whose `value` is a
# (serialized) `EmployeeFilter`. To decide whether such a policy applies to the
# calling actor we reuse the existing employee resolver predicate and intersect
# it with the token's UUID, roughly:
#
#     predicate = and_(
#         employee_predicate(info, deserialized_filter),
#         BrugerRegistrering.bruger_id == token.uuid,
#     )
#     applies = await session.scalar(select(exists().where(predicate)))
#
# i.e. "is the current user (token.uuid) among the employees matching this
# filter?". The policies `actor` filter would, for filter-kind actors, run this
# check per policy against the calling actor at permission-check time.
#
# Open questions: how to (de)serialize an EmployeeFilter for storage, and how to
# evaluate many such policies efficiently (per-policy predicate vs. one query).
class PolicyActor(Base):
    __tablename__ = "policy_actor"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The kind of actor attribute to match on: "uuid", "username" or "role".
    kind: Mapped[str]
    # The value the attribute must equal (a uuid string, username or role name).
    value: Mapped[str]

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="actors")

    # A given (kind, value) is declared at most once per policy, which makes
    # `policy_actor_declare` idempotent.
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
    # all fields. The entities filter is not modelled yet.
    type: Mapped[str]
    field: Mapped[str]
    # Optional CEL (Common Expression Language) condition gating the grant: the
    # rule only applies when this boolean expression evaluates true against the
    # request context (see mora/graphapi/policy_cel.py). A null condition is
    # unconditional. The same (type, field) may carry several conditions, each a
    # separate rule, granting access if any of them holds.
    condition: Mapped[str | None]
    # Optional entity filter further restricting the grant to a specific set of
    # objects: a (serialized) MO filter (e.g. an `ITUserFilter`) evaluated
    # against the entity being accessed. For an entity-targeting mutation like
    # `ituser_update`, the rule only grants when the mutated object's uuid is
    # among the objects the filter matches (see `_entity_filter_grants`). A null
    # filter places no entity restriction.
    filter: Mapped[str | None]

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="rules")

    # A given (type, field, condition, filter) is declared at most once per
    # policy, which makes `policy_rule_declare` idempotent. NULLs are treated as
    # equal so a filter-less, unconditional rule is also deduplicated (requires
    # PostgreSQL >= 15).
    __table_args__ = (
        UniqueConstraint(
            "policy_fk",
            "type",
            "field",
            "condition",
            "filter",
            name="uq_policy_rule",
            postgresql_nulls_not_distinct=True,
        ),
    )
