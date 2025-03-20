# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from base64 import b64decode, b64encode
from datetime import datetime
from enum import Enum
from functools import partial
from textwrap import dedent
from typing import Self
from uuid import UUID

import sqlalchemy
import strawberry
from fastramqpi.ra_utils.apply import apply
from more_itertools import bucket
from pydantic import BaseModel
from sqlalchemy import select
from starlette_context import context
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from mora.access_log import access_log
from mora.db import AccessLogOperation as AccessLogOperation
from mora.db import AccessLogRead as AccessLogRead
from mora.db import AsyncSession
from mora import db

from ..latest.filters import gen_filter_string
from ..latest.filters import gen_filter_table
from .paged import CursorType
from .paged import LimitType
from .resolvers import get_sqlalchemy_date_interval


# Listeners
# ---------


@strawberry.type(description="Event listeners")
class Listener:
    uuid: UUID = strawberry.field(description="ID of the listener")
    owner: UUID = strawberry.field(
        description="Owner of the listener. Only the owner can read the listeners' events."
    )
    user_key: str = strawberry.field(description="something about idempotency")
    namespace: str
    routing_key: str = strawberry.field(description="The routing key for the listeners")


@strawberry.input(description="Listener filter.")
class ListenerFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    owners: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Owner", "owners")
    )
    routing_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Routing key", "routing_keys"),
    )


async def listener_resolver(
    info: Info,
    filter: ListenerFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[Listener]:
    if filter is None:
        filter = ListenerFilter()

    clauses = []

    if filter.uuids is not None:
        clauses.append(db.Listener.pk.in_(filter.uuids))

    if filter.owners is not None:
        clauses.append(db.Listener.owner.in_(filter.owners))

    if filter.routing_keys is not None:
        clauses.append(db.Listener.routing_key.in_(filter.routing_keys))

    # TODO: pagination can't work here?

    session = info.context["session"]
    result = list(await session.scalars(select(db.Listener).where(*clauses)))

    return [
        Listener(
            uuid=listener.pk,
            user_key=listener.user_key,
            owner=listener.owner,
            namespace=listener.namespace,
            routing_key=listener.routing_key,
        )
        for listener in result
    ]


class EventToken(BaseModel):
    uuid: UUID
    last_tried: datetime

    @staticmethod
    def serialize(value: "EventToken") -> str:
        result = f"{value.uuid}.{value.last_tried.isoformat()}"
        return b64encode(result.encode()).decode("ascii")

    @staticmethod
    def deserialize(opaque: str) -> "EventToken":
        uuid, timestamp = b64decode(opaque).decode().split(".", 1)
        return EventToken(uuid=UUID(uuid), last_tried=datetime.fromisoformat(timestamp))


OpaqueEventToken = strawberry.scalar(
    EventToken,
    serialize=EventToken.serialize,
    parse_value=EventToken.deserialize,
    description=dedent(
        """\
        Event tokens are used for event related operations, such as acknowledgment.
        
        This is an opaque value and as such, you should *never* depend on the actual value.

        You should not store it for later or construct it yourself, as newer MO versions can change the underlying implementation.
        """
    ),
)


@strawberry.type(description="Event")
class Event:
    # uuid: UUID = strawberry.field(description="ID of the event")  # do we even need this?
    subject: str = strawberry.field(
        description="An identifier of the subject. When it is a MO subject, it is always a UUID."
    )
    token: OpaqueEventToken = strawberry.field(description="hallelujah")


@strawberry.input(description="Listener filter.")
class EventFilter:
    listener: UUID = strawberry.field(description="ID of listener")


async def event_resolver(
    info: Info,
    filter: EventFilter,
) -> Event | None:
    query = (
        select(db.Event)
        .where(
            db.Event.listener_fk == filter.listener,
            db.Event.silenced == sqlalchemy.true(),
        )
        .order_by(
            db.Event.priority.asc(),
            db.Event.last_tried.asc(),
        )
        .limit(1)
    )
    print("QUERY", query.compile())

    session = info.context["session"]
    result = await session.scalar(query)
    if result is None:
        return None
    return Event(
        subject=result.subject,
        token=EventToken(uuid=result.pk, last_tried=result.last_tried),
    )
