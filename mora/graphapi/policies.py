# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

import strawberry
from sqlalchemy import select

from mora import db
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo

from .paged import CursorType
from .paged import LimitType
from .paged import ObjectsAndCursor
from .paged import paginate


@strawberry.type(
    description=(
        "An access policy. A policy applies to a collection of actors and "
        "grants them access to a number of resources."
    )
)
class Policy:
    uuid: UUID = strawberry.field(description="UUID of the policy.")
    name: str = strawberry.field(description="Name of the policy.")
    description: str | None = strawberry.field(
        description="Description of the policy."
    )
    start: datetime = strawberry.field(description="Start of the policy's validity.")
    end: datetime | None = strawberry.field(
        description="End of the policy's validity, if applicable."
    )


def _to_policy(policy: "db.Policy") -> Policy:
    return Policy(
        uuid=policy.id,
        name=policy.name,
        description=policy.description,
        start=policy.start,
        end=policy.end,
    )


async def policy_resolver(
    info: MOInfo,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    # No filtering is supported (yet); we always read every policy across all of
    # time (-inf to inf), exposing only keyset pagination via limit/cursor.
    query = select(db.Policy.id).order_by(db.Policy.id)
    session: AsyncSession = info.context.session
    uuids, next_cursor = await paginate(session, query, db.Policy.id, limit, cursor)

    result = await session.scalars(
        select(db.Policy).where(db.Policy.id.in_(uuids)).order_by(db.Policy.id)
    )
    return ObjectsAndCursor(
        objects=[_to_policy(policy) for policy in result],
        next_cursor=next_cursor,
    )
