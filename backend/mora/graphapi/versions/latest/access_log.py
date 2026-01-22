# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from enum import Enum
from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry
from fastramqpi.ra_utils.apply import apply
from more_itertools import bucket
from sqlalchemy import select
from starlette_context import context
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from mora.access_log import access_log
from mora.db import AccessLogOperation as AccessLogOperation
from mora.db import AccessLogRead as AccessLogRead
from mora.db import AsyncSession

from ...context import MOInfo
from ..latest.filters import gen_filter_string
from ..latest.filters import gen_filter_table
from .actor import Actor
from .actor import actor_uuid_to_actor
from .paged import CursorType
from .paged import LimitType
from .resolvers import get_sqlalchemy_date_interval


def get_access_log_loaders(session: AsyncSession) -> dict[str, DataLoader]:
    """Return dataloaders required for access log functionality.

    Args:
        session: The DB session to run queries on.

    Returns:
        A dictionary of loaders required for access log functionality.
    """
    return {
        "access_log_read_loader": DataLoader(
            load_fn=partial(access_log_read_loader, session)
        )
    }


async def access_log_read_loader(
    session: AsyncSession, keys: list[UUID]
) -> list[list[UUID]]:
    """Load UUIDs registered as read for the given operation.

    Args:
        session: The database session to run queries on.
        keys: List of operation UUIDs to lookup read UUIDs for.

    Returns:
        A list containing a sublist for each UUID in keys.
        Each sublist containing the UUIDs read by the operation.
    """
    query = select(AccessLogRead.operation_id, AccessLogRead.uuid).where(
        AccessLogRead.operation_id.in_(keys)
    )
    result = list(await session.execute(query))
    buckets = bucket(result, apply(lambda operation_id, _: operation_id))
    return [[uuid for _, uuid in buckets[key]] for key in keys]


@strawberry.enum
class AccessLogModel(Enum):
    ACCESS_LOG = "AccessLog"
    PERSON = "Bruger"
    FACET = "Facet"
    IT_SYSTEM = "ItSystem"
    CLASS = "Klasse"
    ORGANISATION = strawberry.enum_value(
        "Organisation",
        deprecation_reason="The root organisation concept will be removed in a future version of OS2mo.",
    )
    ORGANISATION_UNIT = "OrganisationEnhed"
    ORGANISATION_FUNCTION = "OrganisationFunktion"


@strawberry.type(
    description=dedent(
        """\
        Access log entry.

        Mostly useful for auditing purposes seeing when data-reads were done and by whom.
        """
    )
)
# Intentionally not including operation and arguments from the underlying table
# Once LoRa's API and the Service API has been removed, we may want to log the GraphQL query
class AccessLog:
    id: UUID = strawberry.field(
        description=dedent(
            """\
            UUID of the access log entry itself.
            """
        )
    )

    time: datetime = strawberry.field(
        description=dedent(
            """\
        When the read occured.

        Examples:
        * `"1970-01-01T00:00:00.000000+00:00"`
        * `"2019-12-18T12:55:15.348614+00:00"`
        """
        )
    )

    actor: UUID = strawberry.field(
        description=dedent(
            """\
        UUID of the actor (integration or user) who changed the data.

        Note:
        Currently mostly returns `"42c432e8-9c4a-11e6-9f62-873cf34a735f"`.
        Will eventually contain for the UUID of the integration or user who mutated data, based on the JWT token.
        """
        ),
        deprecation_reason="Use actor_object.",
    )

    @strawberry.field(
        description=dedent(
            """\
            Object for the actor (integration or user) who changed the data.
            """
        )
    )
    async def actor_object(self, root: "AccessLog", info: Info) -> Actor:
        return actor_uuid_to_actor(root.actor)

    # Name of the entity model
    model: AccessLogModel = strawberry.field(
        description=dedent(
            """\
        Model of the modified entity.
        """
        )
    )

    # UUID of the modified entity
    @strawberry.field(
        description=dedent(
            """\
        UUIDs of entities that were read.
        """
        )
    )
    async def uuids(self, info: MOInfo) -> list[UUID]:
        return await info.context.dataloaders.access_log_read_loader.load(self.id)


@strawberry.input(description="Access log log filter.")
class AccessLogFilter:
    ids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("ID", "ids")
    )

    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )

    actors: list[UUID] | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Filter access log events by their reading actor.

            Can be used to select all data read by a particular user or integration.
            """
        )
        + gen_filter_table("actors"),
    )

    models: list[AccessLogModel] | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Filter access log events by their model type.

            Can be used to select all reads for a data type.

            Can be one of:
            * `"AccessLog"`
            * `"Bruger"`
            * `"Facet"`
            * `"ItSystem"`
            * `"Klasse"`
            * `"Organisation"`
            * `"OrganisationEnhed"`
            * `"OrganisationFunktion"`
            """
        )
        + gen_filter_table("models"),
    )

    start: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their starting validity.",
    )
    end: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their ending validity.",
    )


async def access_log_resolver(
    info: Info,
    filter: AccessLogFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[AccessLog]:
    if filter is None:
        filter = AccessLogFilter()

    query = select(AccessLogOperation)
    if filter.ids is not None:  # pragma: no cover
        query = query.where(AccessLogOperation.id.in_(filter.ids))

    if filter.uuids is not None:
        subquery = select(AccessLogRead.operation_id).filter(
            AccessLogRead.uuid.in_(filter.uuids)
        )
        query = query.where(AccessLogOperation.id.in_(subquery))

    if filter.actors is not None:
        query = query.where(AccessLogOperation.actor.in_(filter.actors))

    if filter.models is not None:
        models = [model.value for model in filter.models]
        query = query.where(AccessLogOperation.model.in_(models))

    if filter.start is not None or filter.end is not None:  # pragma: no cover
        start, end = get_sqlalchemy_date_interval(filter.start, filter.end)
        query = query.where(AccessLogOperation.time.between(start, end))

    # Pagination
    if cursor:
        # Make sure we only see objects created before pagination started
        query = query.where(AccessLogOperation.time <= cursor.registration_time)
    # Order by time, then by UUID so the order of pagination is well-defined
    query = query.order_by(AccessLogOperation.time, AccessLogOperation.id)
    if limit is not None:
        # Fetch one extra element to see if there is another page
        query = query.limit(limit + 1)
    query = query.offset(cursor.offset if cursor else 0)

    session: AsyncSession = info.context["session"]
    result = list(await session.scalars(query))
    access_log(
        session,
        "resolve_accesslog",
        "AccessLog",
        {
            "limit": limit,
            "cursor": cursor,
            "uuids": filter.uuids,
            "actors": filter.actors,
            "models": filter.models,
            "start": filter.start,
            "end": filter.end,
        },
        [accesslog.id for accesslog in result],
    )

    if limit is not None:
        # Not enough results == no more pages
        if len(result) <= limit:
            context["lora_page_out_of_range"] = True
        # Strip the extra element that was only used for page-checking
        elif len(result) == limit + 1:
            result = result[:-1]

    return [
        AccessLog(
            id=accesslog.id,
            time=accesslog.time,
            actor=accesslog.actor,
            model=AccessLogModel(accesslog.model),
        )
        for accesslog in result
    ]
