# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The policies and their rules as GraphQL types."""

from collections.abc import Sequence
from textwrap import dedent
from uuid import UUID

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mora import db
from mora.db import AsyncSession
from mora.db import Collection
from mora.graphapi.context import MOInfo
from mora.graphapi.filters import gen_filter_string
from mora.graphapi.graphql_utils import Field
from mora.graphapi.graphql_utils import MutatorName
from mora.graphapi.graphql_utils import Role
from mora.graphapi.policy_cel import CEL
from mora.graphapi.version import Version

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate

strawberry.enum(
    Collection,
    description="A collection a read rule may grant access to.",
)
strawberry.enum(
    Version,
    name="GraphQLVersion",
    description="A version of the GraphQL schema, which the condition filters of a rule are written in.",
)


@strawberry.type(
    description="Grants conditional access to the specified fields on a collection."
)
class PolicyReadRule:
    collection: Collection = strawberry.field(
        description="The collection field access is granted on."
    )
    fields: list[Field] = strawberry.field(description="The fields that are granted.")
    condition: CEL = strawberry.field(
        description=dedent(
            """\
            CEL expression evaluating to either a boolean, or a filter naming the
            entities that fields are granted on.

            `true` grants the fields of every entity. `false` grants nothing.
            """
        )
    )
    graphql_version: Version = strawberry.field(
        description="The GraphQL version the condition filter is written in."
    )


@strawberry.type(description="Grants conditional access to the specified mutator.")
class PolicyWriteRule:
    mutator: MutatorName = strawberry.field(description="The mutator granted.")
    condition: CEL = strawberry.field(
        description=dedent(
            """\
            CEL expression evaluating to either a boolean, or a
            `{collection, filter}` map naming what must exist for the mutator to be
            granted. Combine maps with `{or: [...]}`, `{and: [...]}` and `{not: ...}`.

            `true` grants the mutator outright. `false` grants nothing.
            """
        )
    )
    graphql_version: Version = strawberry.field(
        description="The GraphQL version the condition filters are written in."
    )


@strawberry.type(description="Policies assign meaning to roles.")
class Policy:
    uuid: UUID = strawberry.field(description="UUID of the policy.")
    name: str = strawberry.field(description="Unique name of the policy.")
    description: str = strawberry.field(description="Description of the policy.")
    active: bool = strawberry.field(
        description=(
            "Whether the policy is active. "
            "Inactive policies are not considered for access control."
        )
    )
    role: Role = strawberry.field(description="The role which activates the policy.")
    managed: bool = strawberry.field(
        description=(
            "Whether MO manages the policy. MO managed policies cannot be modified."
        )
    )
    read_rules: list[PolicyReadRule] = strawberry.field(
        description="The collections the policy grants access to."
    )
    write_rules: list[PolicyWriteRule] = strawberry.field(
        description="The mutators the policy grants access to."
    )


@strawberry.input(description="Policy filter.")
class PolicyFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    names: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Name", "names")
    )
    roles: list[Role] | None = strawberry.field(
        default=None, description=gen_filter_string("Role", "roles")
    )
    active: bool | None = strawberry.field(
        default=None, description="Filter based on whether the policy is active."
    )


async def load_policies(session: AsyncSession, uuids: Sequence[UUID]) -> list[Policy]:
    """Load the policies of the uuids along with their rules."""
    policies = await session.scalars(
        select(db.Policy)
        .where(db.Policy.pk.in_(uuids))
        .order_by(db.Policy.pk)
        .options(
            selectinload(db.Policy.read_rules).selectinload(db.PolicyReadRule.fields),
            selectinload(db.Policy.write_rules),
        )
    )
    return [
        Policy(
            uuid=policy.pk,
            name=policy.name,
            description=policy.description,
            active=policy.active,
            role=policy.role,
            managed=policy.managed,
            read_rules=[
                PolicyReadRule(
                    collection=rule.collection,
                    fields=[field.field for field in rule.fields],
                    condition=rule.condition,
                    graphql_version=rule.graphql_version,
                )
                for rule in policy.read_rules
            ],
            write_rules=[
                PolicyWriteRule(
                    mutator=rule.mutator,
                    condition=rule.condition,
                    graphql_version=rule.graphql_version,
                )
                for rule in policy.write_rules
            ],
        )
        for policy in policies
    ]


async def policy_resolver(
    info: MOInfo,
    filter: PolicyFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = PolicyFilter()

    query = select(db.Policy.pk).order_by(db.Policy.pk)
    if filter.uuids is not None:
        query = query.where(db.Policy.pk.in_(filter.uuids))
    if filter.names is not None:
        query = query.where(db.Policy.name.in_(filter.names))
    if filter.roles is not None:
        query = query.where(db.Policy.role.in_(filter.roles))
    if filter.active is not None:
        query = query.where(db.Policy.active == filter.active)

    session: AsyncSession = info.context.session
    uuids, next_cursor = await paginate(session, query, db.Policy.pk, limit, cursor)
    return ObjectsAndCursor(
        objects=await load_policies(session, uuids), next_cursor=next_cursor
    )
