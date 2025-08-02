# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from base64 import b64decode
from base64 import b64encode
from textwrap import dedent
from uuid import UUID

import sqlalchemy
import strawberry
from more_itertools import one
from pydantic import BaseModel
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import update
from strawberry.types import Info

from mora import db
from mora.auth.middleware import get_authenticated_user
from mora.db import AsyncSession

from ..latest.filters import gen_filter_string
from .paged import CursorType
from .paged import LimitType
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .schema import uuid2list
from .seed_resolver import seed_resolver


@strawberry.input(description="Listener filter.")
class NamespaceFilter:
    names: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("Name", "names")
    )
    owners: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Owner", "owners")
    )
    public: bool | None = strawberry.field(default=None)

    def where_clauses(self: "NamespaceFilter") -> list[ColumnElement[bool]]:
        clauses: list[ColumnElement] = []

        if self.names is not None:
            clauses.append(db.Namespace.name.in_(self.names))

        if self.owners is not None:
            clauses.append(db.Namespace.owner.in_(self.owners))

        if self.public is not None:
            clauses.append(db.Namespace.public == self.public)

        return clauses


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
    namespaces: NamespaceFilter | None = strawberry.field(
        default=None, description="Only match listeners in this namespace"
    )

    def where_clauses(self: "ListenerFilter") -> list[ColumnElement[bool]]:
        clauses: list[ColumnElement] = []

        if self.uuids is not None:
            clauses.append(db.Listener.pk.in_(self.uuids))

        if self.owners is not None:  # pragma: no cover
            clauses.append(db.Listener.owner.in_(self.owners))

        if self.routing_keys is not None:
            clauses.append(db.Listener.routing_key.in_(self.routing_keys))

        if self.namespaces is not None:  # pragma: no cover
            clauses.append(db.Listener.namespace_fk == db.Namespace.name)
            clauses.extend(self.namespaces.where_clauses())

        return clauses


@strawberry.input(description="Event filter.")
class FullEventFilter:
    listeners: ListenerFilter | None = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None
    silenced: bool | None = strawberry.field(
        default=None,
        description="Filter based on silence status.",
    )


async def full_event_resolver(
    info: Info,
    filter: FullEventFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list["FullEvent"]:
    if filter is None:
        filter = FullEventFilter()

    clauses = [
        db.Event.listener_fk == db.Listener.pk,
    ]

    # Only resolve the owners own events _unless_ they have the
    # "read_event_all" permission.
    token = await info.context["get_token"]()
    if "read_event_all" not in token.realm_access.roles:
        owner = get_authenticated_user()
        clauses.append(db.Listener.owner == owner)

    if filter.listeners is not None:
        clauses.extend(filter.listeners.where_clauses())

    if filter.subjects is not None:
        clauses.append(db.Event.subject.in_(filter.subjects))

    if filter.priorities is not None:
        clauses.append(db.Event.priority.in_(filter.priorities))

    if filter.silenced is not None:
        clauses.append(db.Event.silenced == filter.silenced)

    query = (
        select(db.Event)
        .where(*clauses)
        .order_by(
            db.Event.priority.asc(),
            db.Event.last_tried.asc(),
        )
    )
    print(query)

    if limit is not None:  # pragma: no cover
        query = query.limit(limit)
    # This doesn't actually work correctly. It is hard to do pagination
    # correctly, so for now we just do this super naively. This resolver is
    # only used by humans, not by integrations.
    query = query.offset(cursor.offset if cursor else 0)

    session: AsyncSession = info.context["session"]
    result = await session.scalars(query)
    print(list(result))
    return [
        FullEvent(
            subject=event.subject,
            priority=event.priority,
            silenced=event.silenced,
            listener_uuid=event.listener_fk,
        )
        for event in result
    ]


async def listener_resolver(
    info: Info,
    filter: ListenerFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list["Listener"]:
    if filter is None:  # pragma: no cover
        filter = ListenerFilter()

    query = select(db.Listener).where(*filter.where_clauses())

    if limit is not None:
        query = query.limit(limit)  # pragma: no cover
    # This doesn't actually work correctly. It is hard to do pagination
    # correctly, so for now we just do this super naively. This resolver is
    # only used by humans, not by integrations.
    query = query.offset(cursor.offset if cursor else 0)

    session: AsyncSession = info.context["session"]
    result = list(await session.scalars(query))

    return [
        Listener(
            uuid=listener.pk,
            user_key=listener.user_key,
            owner=listener.owner,
            routing_key=listener.routing_key,
            namespace_fk=listener.namespace_fk,
        )
        for listener in result
    ]


async def namespace_resolver(
    info: Info,
    filter: NamespaceFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list["Namespace"]:
    if filter is None:  # pragma: no cover
        filter = NamespaceFilter()

    query = select(db.Namespace).where(*filter.where_clauses())

    if limit is not None:
        query = query.limit(limit)  # pragma: no cover
    # This doesn't actually work correctly. It is hard to do pagination
    # correctly, so for now we just do this super naively. This resolver is
    # only used by humans, not by integrations.
    query = query.offset(cursor.offset if cursor else 0)

    session: AsyncSession = info.context["session"]
    result = list(await session.scalars(query))

    return [
        Namespace(
            name=namespace.name,
            owner=namespace.owner,
            public=namespace.public,
        )
        for namespace in result
    ]


@strawberry.type(
    description=dedent(
        """\
        Event namespace.

        Event namespaces can be used to create other event exchanges, than the one OS2mo comes with.

        You do not need to think about namespaces if you only receive events from OS2mo.
    """
    )
)
class Namespace:
    name: str = strawberry.field(description="Name of the namespace - unique.")
    owner: UUID = strawberry.field(
        description="Owner of the namespace. If the namespace isn't public; only the owner can create listeners in it."
    )
    public: bool = strawberry.field(
        description="Whether others can create listeners in the namespace"
    )

    listeners: list["Listener"] = strawberry.field(
        resolver=seed_resolver(
            listener_resolver,
            {"namespaces": lambda root: NamespaceFilter(names=[root.name])},
        ),
        description="Listeners for this namespace",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_namespace"),
        ],
    )


@strawberry.type(description="Event listeners.")
class Listener:
    uuid: UUID = strawberry.field(description="ID of the listener.")
    owner: UUID = strawberry.field(
        description="Owner of the listener. Only the owner can fetch the listeners' events."
    )
    user_key: str = strawberry.field(
        description="The user_key for a listener is a user-supplied identifier. It must be unique per (namespace, owner). It is useful when a consumer needs to listen to the same (namespace, routing_key) multiple times."
    )
    routing_key: str = strawberry.field(description="The routing key for the listeners")

    namespace_fk: strawberry.Private[str]

    @strawberry.field(
        description="The namespace of the listener.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_namespace"),
        ],
    )
    async def namespace(root: "Listener", info: strawberry.Info) -> Namespace:
        # coverage: pause
        filter = NamespaceFilter(names=[root.namespace_fk])
        result = await namespace_resolver(info, filter)
        return one(result)
        # coverage: unpause

    events: list["FullEvent"] = strawberry.field(
        resolver=seed_resolver(
            full_event_resolver,
            {"listeners": lambda root: ListenerFilter(uuids=uuid2list(root.uuid))},
        ),
        description="Pending events for this listener. Use `event_fetch` to consume events.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event"),
        ],
    )


@strawberry.type(description="FullEvent")
class FullEvent:
    # Do not add EventToken to this class.

    subject: str = strawberry.field(
        description="An identifier of the subject. All subjects in OS2mo have UUIDs as identifier."
    )
    priority: int = strawberry.field(
        description=f"The priority of an event. Lower means higher priority. The default is {db.events.DEFAULT_PRIORITY}."
    )
    silenced: bool = strawberry.field(
        description="Whether the event is silenced. Silenced event cannot be read by `event_fetch`."
    )
    listener_uuid: strawberry.Private[UUID]

    @strawberry.field(
        description="The listener that will receive this event.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_listener"),
        ],
    )
    async def listener(root: "FullEvent", info: strawberry.Info) -> Listener:
        # coverage: pause
        filter = ListenerFilter(uuids=[root.listener_uuid])
        result = await listener_resolver(info, filter)
        return one(result)
        # coverage: unpause


class EventToken(BaseModel):
    uuid: UUID
    generation: UUID

    @staticmethod
    def serialize(value: "EventToken") -> str:
        result = f"{value.uuid}.{value.generation}"
        return b64encode(result.encode()).decode("ascii")

    @staticmethod
    def deserialize(opaque: str) -> "EventToken":
        try:
            uuid, generation = b64decode(opaque).decode().split(".", 1)
            return EventToken(uuid=UUID(uuid), generation=UUID(generation))
        except Exception:
            raise ValueError("Could not parse EventToken")


EventTokenType: type[EventToken] = strawberry.scalar(
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
        Event.

        You need to use the `token` to acknowledge that the event has been handled properly by calling `event_acknowledge`.

        Your integration is supposed to handle *all* events that the listener subscribes to. If your integration does not need to do anything for a particular event, it still needs to be acknowledged.

        You might see events in the `events` collection that you do not appear to receive when calling `event_fetch`. This is because OS2mo will not spam you with the same event over and over if it fails.
        """
    )
)
class Event:
    subject: str = strawberry.field(
        description='An identifier of the subject. All subjects in the (default) "mo" namespace have UUIDs as identifier.'
    )
    priority: int = strawberry.field(description="Priority of the event.")
    token: EventTokenType = strawberry.field(
        description=dedent(
            """\
            EventTokens are opaque tokens needed to acknowledge events.
            """
        )
    )


@strawberry.input(description="Event filter.")
class EventFilter:
    listener: UUID = strawberry.field(description="ID of listener.")


async def event_resolver(
    info: Info,
    filter: EventFilter,
) -> Event | None:
    owner = get_authenticated_user()
    subquery = (
        select(db.Event.pk)
        .where(
            db.Event.listener_fk == filter.listener,
            db.Event.silenced == sqlalchemy.false(),
            # Check for owner. You simply won't get anything if you query
            # someone elses listener.
            db.Event.listener_fk == db.Listener.pk,
            db.Listener.owner == owner,
            # Make sure we do not spam the client with events it has already
            # tried but failed to acknowledge. Exponential backoff between 3
            # minutes and 1 day. We start by trying every 3 minutes 7 times.
            db.Event.last_tried
            < func.now()
            - func.greatest(
                func.make_interval(mins=3),
                func.least(
                    func.make_interval(
                        # Clamp to avoid integer overflow
                        secs=func.power(2, func.least(db.Event.fetched_count, 32))
                    ),
                    func.make_interval(days=1),
                ),
            ),
        )
        .order_by(db.Event.priority.asc(), db.Event.fetched_count.asc())
        .limit(1)
        .cte()
    )
    query = (
        update(db.Event)
        .where(db.Event.pk == subquery.c.pk)
        .values(last_tried=func.now(), fetched_count=db.Event.fetched_count + 1)
        .returning(db.Event)
    )
    session: AsyncSession = info.context["session"]
    result = await session.scalar(query)
    if result is None:
        # We sleep a bit when there are no event to reduce the load on the
        # database from integrations spamming for events. Subject to change for
        # sure.
        await asyncio.sleep(0.2)
        return None
    return Event(
        subject=result.subject,
        priority=result.priority,
        token=EventToken(uuid=result.pk, generation=result.generation),
    )
