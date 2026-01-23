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
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

import mora.db

from . import AsyncSession
from ._common import Base

# If this is changed, remember to update the documentation.
DEFAULT_PRIORITY = 10000


METRIC_EVENTS = Gauge(
    "os2mo_events",
    "Events",
    ["owner", "user_key", "ns", "routing_key", "silenced"],
)

METRIC_OLD_EVENTS = Gauge(
    "os2mo_event_oldest",
    "Timestamp of oldest event per listener",
    ["owner", "user_key", "ns", "routing_key", "silenced"],
)

METRIC_ACKNOWLEDGED_EVENTS = Counter(
    "os2mo_event_acknowledged",
    "Acknowledged events",
    ["owner", "user_key", "ns", "routing_key"],
)

METRIC_SENT_EVENTS = Counter(
    "os2mo_event_sent",
    "Sent events",
    ["ns", "routing_key"],
)


class Namespace(Base):
    __tablename__ = "event_namespace"

    name: Mapped[str] = mapped_column(primary_key=True)
    # Most often, this is the integration UUID from Keycloak. It can be the
    # UUID of a user as well.
    owner: Mapped[UUID]
    public: Mapped[bool]
    listeners: Mapped[list["Listener"]] = relationship(back_populates="namespace")


class Listener(Base):
    __tablename__ = "event_listener"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_key: Mapped[str]
    # Owner is often the same as the namespace owner, but might differ with
    # public namespaces.
    owner: Mapped[UUID]
    routing_key: Mapped[str]

    namespace_fk: Mapped[str] = mapped_column(ForeignKey("event_namespace.name"))
    namespace: Mapped[Namespace] = relationship(back_populates="listeners")

    events: Mapped[list["Event"]] = relationship(back_populates="listener")

    __table_args__ = (
        UniqueConstraint(
            "user_key",
            "owner",
            "namespace_fk",
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

    listener_fk: Mapped[UUID] = mapped_column(ForeignKey("event_listener.pk"))
    listener: Mapped[Listener] = relationship(back_populates="events")

    __table_args__ = (
        UniqueConstraint("listener_fk", "subject", name="uq_listener_subject"),
    )


async def add_event(
    session: AsyncSession,
    *,
    namespace: str,
    routing_key: str,
    subject: str,
    priority: int = DEFAULT_PRIORITY,
    listener_uuid: UUID | None = None,
    listener_owner: UUID | None = None,
) -> None:
    matching_listeners = [
        Listener.namespace_fk == namespace,
        Listener.routing_key == routing_key,
    ]

    if listener_uuid is not None:
        matching_listeners.append(Listener.pk == listener_uuid)
    if listener_owner is not None:
        matching_listeners.append(Listener.owner == listener_owner)

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
            ).where(Listener.pk.in_(select(Listener.pk).where(*matching_listeners))),
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
                # Reset exponential backoff.
                "fetched_count": text("0"),
            },
        )
    )

    await session.execute(stmt)

    METRIC_SENT_EVENTS.labels(ns=namespace, routing_key=routing_key).inc()


def setup_event_metrics(instrumentator: Instrumentator) -> None:
    async def oldest_event_per_listener(info) -> None:
        url_path = info.request.url.path
        if not (url_path.endswith("metrics") or url_path.endswith("metrics/")):
            return
        METRIC_OLD_EVENTS.clear()
        async with (
            mora.db._get_sessionmaker(info.request)() as session,
            session.begin(),
        ):
            query = (
                select(
                    Listener,
                    func.min(
                        sqlalchemy.case(
                            (Event.silenced == sqlalchemy.false(), Event.created_at)
                        )
                    ),
                    func.min(
                        sqlalchemy.case(
                            (Event.silenced == sqlalchemy.true(), Event.created_at)
                        )
                    ),
                )
                .join(Listener.events)
                .group_by(Listener.pk)
            )

            result = await session.execute(query)
            # coverage: pause
            for listener, active, silenced in result.all():
                if active is not None:
                    METRIC_OLD_EVENTS.labels(
                        owner=listener.owner,
                        user_key=listener.user_key,
                        ns=listener.namespace_fk,
                        routing_key=listener.routing_key,
                        silenced="false",
                    ).set(int(active.timestamp()))
                if silenced is not None:
                    METRIC_OLD_EVENTS.labels(
                        owner=listener.owner,
                        user_key=listener.user_key,
                        ns=listener.namespace_fk,
                        routing_key=listener.routing_key,
                        silenced="true",
                    ).set(int(silenced.timestamp()))
            # coverage: unpause

    async def count_events(info) -> None:
        url_path = info.request.url.path
        if not (url_path.endswith("metrics") or url_path.endswith("metrics/")):
            return
        METRIC_EVENTS.clear()
        async with (
            mora.db._get_sessionmaker(info.request)() as session,
            session.begin(),
        ):
            query = (
                select(
                    Listener,
                    func.count(Event.pk).filter(Event.silenced == sqlalchemy.true()),
                    func.count(Event.pk).filter(Event.silenced == sqlalchemy.false()),
                )
                # We outerjoin so we still get the metric even if there are no events.
                # This ensures that our dataseries go to zero instead of disappearing.
                .outerjoin(
                    Event,
                    Listener.pk == Event.listener_fk,
                )
                .group_by(Listener.pk)
            )

            result = await session.execute(query)

            for listener, silenced, active in result.all():
                METRIC_EVENTS.labels(
                    owner=listener.owner,
                    user_key=listener.user_key,
                    ns=listener.namespace_fk,
                    routing_key=listener.routing_key,
                    silenced="true",  # prometheus does not have booleans
                ).set(silenced)
                METRIC_EVENTS.labels(
                    owner=listener.owner,
                    user_key=listener.user_key,
                    ns=listener.namespace_fk,
                    routing_key=listener.routing_key,
                    silenced="false",  # prometheus does not have booleans
                ).set(active)

    instrumentator.add(oldest_event_per_listener)
    instrumentator.add(count_events)
