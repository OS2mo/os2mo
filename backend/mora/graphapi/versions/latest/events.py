# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from base64 import b64decode, b64encode
from datetime import datetime
from enum import Enum
from functools import partial
from textwrap import dedent
from typing import Self
from uuid import UUID

from graphql.pyutils import description
import sqlalchemy
import strawberry
from fastramqpi.ra_utils.apply import apply
from more_itertools import bucket
from pydantic import BaseModel
from sqlalchemy import select
from starlette_context import context
from strawberry import UNSET
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
from .schema import to_one
from .schema import uuid2list
from .resolvers import get_sqlalchemy_date_interval
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .seed_resolver import seed_resolver


@strawberry.type(description="Event listeners")
class Listener:
    uuid: UUID = strawberry.field(description="ID of the listener")
    owner: UUID = strawberry.field(
        description="Owner of the listener. Only the owner can read the listeners' events."
    )
    user_key: str = strawberry.field(description="something about idempotency")
    namespace: str
    routing_key: str = strawberry.field(description="The routing key for the listeners")

    # events: list["FullEvent"] = strawberry.field(
    #     resolver=to_list(seed_resolver(full_event_resolver, {"uuids": lambda root: uuid2list(root.uuid)})),
    #     description="Pending events for this listener.",
    #     permission_classes=[
    #         IsAuthenticatedPermission,
    #         gen_read_permission("event"),
    #     ],

    # )


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

    query = select(db.Listener).where(*clauses)

    if limit is not None:
        query = query.limit(limit)
    # TODO: this is not actually stable as we don't use registration time.
    query = query.offset(cursor.offset if cursor else 0)

    session = info.context["session"]
    result = list(await session.scalars(query))

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


@strawberry.type(description="FullEvent")
class FullEvent:
    uuid: UUID = strawberry.field(description="ID of the event")
    subject: str = strawberry.field(
        description="An identifier of the subject. All subjects in OS2mo have UUIDs as identifier."
    )
    priority: int = strawberry.field(
        description="The priority of an event. Lower means higher priority. The default is 10."
    )
    silenced: bool = strawberry.field(
        description="Whether the event is silenced. Silenced event cannot be read by `event_fetch`."
    )
    listener_uuid: strawberry.Private[UUID]

    @strawberry.field(
        description="The listener that will receive this event.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("listener"),
        ],
    )
    async def listener(root: "FullEvent", info: strawberry.Info) -> Listener:
        filter = ListenerFilter(uuids=[root.listener_uuid])
        result = await listener_resolver(info, filter)
        assert len(result) == 1
        return result[0]


@strawberry.input(description="Listener filter.")
class FullEventFilter:
    listener: ListenerFilter | None = None
    uuids: list[UUID] | None = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None
    silenced: bool | None = strawberry.field(
        default=UNSET,
        description="Filter based on silence status.",
    )


async def full_event_resolver(
    info: Info,
    filter: FullEventFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[FullEvent]:
    if filter is None:
        filter = FullEventFilter()

    clauses = []

    if filter.uuids is not None:
        clauses.append(db.Event.uuid.in_(filter.uuids))

    if filter.subjects is not None:
        clauses.append(db.Event.subject.in_(filter.subjects))

    if filter.priorities is not None:
        clauses.append(db.Event.priority.in_(filter.priorities))

    if filter.silenced is not UNSET:
        clauses.append(db.Event.silenced == filter.silenced)

    query = select(db.Event)

    if clauses:
        query = query.where(*clauses)

    query = query.order_by(
        db.Event.priority.asc(),
        db.Event.last_tried.asc(),
    )
    if limit is not None:
        query = query.limit(limit)
    # TODO: this is not actually stable as we don't use registration time.
    query = query.offset(cursor.offset if cursor else 0)

    session = info.context["session"]
    result = await session.scalars(query)
    return [
        FullEvent(
            uuid=event.pk,
            subject=event.subject,
            priority=event.priority,
            silenced=event.silenced,
            listener_uuid=event.listener_fk,
        )
        for event in result
    ]


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


@strawberry.type(
    description=dedent(
        """\
    Event

    You need to use the `token` to acknowledge that the event has been handled properly by calling `event_acknowledge`.

    Your integration is supposed to handle *all* events that the listener subscribes to. If your integration does not need to do anything for a particular event, it still needs to be acknowledged.

    You might see events in the `events` collection that you do not appear to receive when calling `event_fetch`. This is because OS2mo will not spam you with the same event over and over if it fails.
    """
    )
)
class Event:
    # mention that you can sometimes see unsilenced events in the events
    # collection, that you wont fetch, because MO will not spam you with events
    # you never ack.
    uuid: UUID = strawberry.field(description="ID of the event")
    subject: str = strawberry.field(
        description="An identifier of the subject. All subjects in OS2mo have UUIDs as identifier."
    )
    token: OpaqueEventToken = strawberry.field(
        description=dedent(
            """\
        EventTokens are a completely opaque token needed to acknowledge events. 
        """
        )
    )


@strawberry.input(description="Listener filter.")
class EventFilter:
    listener: UUID = strawberry.field(description="ID of listener")


async def event_resolver(
    info: Info,
    filter: EventFilter,
) -> Event | None:
    # is this actuall the query we want?
    query = (
        select(db.Event)
        .where(
            db.Event.listener_fk == filter.listener,
            db.Event.silenced == sqlalchemy.false(),
        )
        .order_by(
            db.Event.priority.asc(),
            db.Event.last_tried.asc(),
        )
        .limit(1)
    )

    # TODO update last_tried

    session = info.context["session"]
    result = await session.scalar(query)
    if result is None:
        return None
    return Event(
        uuid=result.pk,
        subject=result.subject,
        token=EventToken(uuid=result.pk, last_tried=result.last_tried),
    )
