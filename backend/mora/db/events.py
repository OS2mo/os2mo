# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

import sqlalchemy
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from ._common import Base


class Namespace(Base):
    __tablename__ = "event_namespace"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_key: Mapped[str]
    # Most often, this is the integration UUID from Keycloak. It can be the
    # UUID of a user as well.
    owner: Mapped[UUID]
    events: Mapped[list["Event"]] = relationship(back_populates="listener")



class Listener(Base):
    __tablename__ = "event_listener"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_key: Mapped[str]
    namespace: Mapped[str]
    routing_key: Mapped[str]
    events: Mapped[list["Event"]] = relationship(back_populates="listener")

    __table_args__ = (
        UniqueConstraint(
            "user_key",
            "owner",
            "namespace",
            name="uq_user_key_owner_namespace",
        ),
    )


class Event(Base):
    __tablename__ = "event"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    subject: Mapped[str]
    priority: Mapped[int]
    # We update generation everytime we deduplicate an event to make use the
    # ack doesn't remove the event. This ensure that integration don't miss any
    # events.
    generation: Mapped[UUID]
    # last_tried is the last time the event was returned through a call to
    # `event_fetch`.
    last_tried: Mapped[datetime]
    fetched_count: Mapped[int]
    silenced: Mapped[bool]
    created_at: Mapped[datetime]

    listener_fk: Mapped[UUID] = mapped_column(ForeignKey("listener.pk"))
    listener: Mapped[Listener] = relationship(back_populates="events")

    __table_args__ = (
        UniqueConstraint("listener_fk", "subject", name="uq_listener_subject"),
    )


async def add_event(
    session: AsyncSession,
    namespace: str,
    routing_key: str,
    subject: str,
    priority: int = 10,
) -> None:
    matching_listeners = select(Listener.pk).where(
        Listener.namespace == namespace,
        Listener.routing_key == routing_key,
    )

    stmt = (
        insert(Event)
        .from_select(
            [
                "listener_fk",
                "subject",
                "priority",
            ],
            select(
                Listener.pk,
                literal(subject),
                literal(priority),
            ).where(Listener.pk.in_(matching_listeners)),
        )
        .on_conflict_do_update(
            index_elements=["listener_fk", "subject"],
            # These will be updated when we violate the unique constraint:
            set_={
                # Updating `generation` ensures that clients won't miss an
                # event in the case where a new event arrives while the client
                # is already processing an event for the same subject (the
                # generation is used for acknowledgement in EventToken).
                "generation": text("uuid_generate_v4()"),
                # Update `last_tried`  so the event is send without delay.
                "last_tried": text("'1970-01-01'::timestamptz"),
                # Deduplicate priorities. This deduplicates such that we choose
                # the highest priority event and discard the other.
                "priority": text("least(excluded.priority, event.priority)"),
                # Reset `fetched_count`. New data, new me.
                "fetched_count": text("0"),
            },
        )
    )

    await session.execute(stmt)

    sent_events.labels(namespace=namespace, routing_key=routing_key).inc()


def setup_event_metrics(
    sessionmaker: async_sessionmaker, instrumentator: Instrumentator
) -> None:
    events = Gauge(
        "os2mo_events",
        "Events",
        ["owner", "user_key", "namespace", "routing_key", "silenced"],
    )

    old_events = Gauge(
        "os2mo_event_oldest",
        "Timestamp of oldest event per listener",
        ["owner", "user_key", "namespace", "routing_key", "silenced"],
    )

    async def oldest_event_per_listener(_) -> None:
        async with sessionmaker() as session, session.begin():
            query = (
                select(
                    Listener,
                    func.min(sqlalchemy.case((Event.silenced == sqlalchemy.false(), Event.created_at))),
                    func.min(sqlalchemy.case((Event.silenced == sqlalchemy.true(), Event.created_at))),
                )
                .join(Listener.events)
                .group_by(Listener.pk)
            )

            result = await session.execute(query)
            for listener, active, silenced in result.all():
                if active is not None:
                    old_events.labels(
                        owner=listener.owner,
                        user_key=listener.user_key,
                        namespace=listener.namespace,
                        routing_key=listener.routing_key,
                        silenced="false",
                    ).set(int(active.timestamp()))
                if silenced is not None:
                    old_events.labels(
                        owner=listener.owner,
                        user_key=listener.user_key,
                        namespace=listener.namespace,
                        routing_key=listener.routing_key,
                        silenced="true",
                    ).set(int(silenced.timestamp()))

    async def count_events(_) -> None:
        async with sessionmaker() as session, session.begin():
            query = (select(Listener, func.count(Event.pk), Event.silenced)
                    .join(
                        Event,
                        Listener.pk == Event.listener_fk,
                    )
                    .group_by(Listener.pk, Event.silenced)
                )

            result = await session.execute(query)

            for listener, count, silenced in result.all():
                events.labels(
                    owner=listener.owner,
                    user_key=listener.user_key,
                    namespace=listener.namespace,
                    routing_key=listener.routing_key,
                    silenced=str(silenced).lower(),  # prometheus does not have booleans
                ).set(count)

    instrumentator.add(oldest_event_per_listener)
    instrumentator.add(count_events)


acknowledged_events = Counter(
    "os2mo_event_acknowledged",
    "Acknowledged events",
    ["owner", "user_key", "namespace", "routing_key"],
)

sent_events = Counter(
    "os2mo_event_sent",
    "Sent events",
    ["namespace", "routing_key"],
)
