# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

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


class Listener(Base):
    __tablename__ = "listener"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    user_key: Mapped[str]
    owner: Mapped[UUID]  # integration uuid from Keycloak
    namespace: Mapped[str]
    routing_key: Mapped[str]
    events: Mapped[list["Event"]] = relationship(back_populates="listener")

    __table_args__ = (
        UniqueConstraint(
            "user_key",
            "owner",
            "namespace",
            "routing_key",
            name="uq_user_key_owner_namespace_routing_key",
        ),
    )


class Event(Base):
    __tablename__ = "event"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    subject: Mapped[str]
    priority: Mapped[int]
    last_tried: Mapped[datetime]
    silenced: Mapped[bool]

    listener_fk: Mapped[UUID] = mapped_column(ForeignKey("listener.pk"))
    listener: Mapped[Listener] = relationship(back_populates="events")

    __table_args__ = (
        UniqueConstraint(
            "listener_fk", "subject", "priority", name="uq_listener_subject_priority"
        ),
    )


async def add_event(
    session, namespace: str, routing_key: str, subject: str, priority: int = 10
):
    matching_listeners = select(Listener.pk).where(
        Listener.namespace == namespace,
        Listener.routing_key == routing_key,
    )

    stmt = (
        insert(Event)
        .from_select(
            ["pk", "listener_fk", "subject", "priority", "last_tried", "silenced"],
            select(
                text("uuid_generate_v4()"),
                Listener.pk,
                literal(subject),
                literal(priority),
                text("'1970-01-01'::timestamptz"),  # last_tried
                text("false"),  # silenced
            ).where(Listener.pk.in_(matching_listeners)),
        )
        .on_conflict_do_update(
            index_elements=["listener_fk", "subject", "priority"],
            # When we violate the unique constraint, update `last_tried`.
            # This ensures that clients won't miss an event in the case where
            # a new event arrives while the client is already processing an
            # event for the same subject.
            set_={"last_tried": text("now()")},
        )
    )

    await session.execute(stmt)

    sent_events.labels(namespace=namespace, routing_key=routing_key).inc()


def setup_event_metrics(
    sessionmaker: async_sessionmaker, instrumentator: Instrumentator
) -> None:
    silenced_events = Gauge(
        "os2mo_event_silenced",
        "Silenced events",
        ["owner", "user_key", "namespace", "routing_key"],
    )

    active_events = Gauge(
        "os2mo_event_active",
        "Active events",
        ["owner", "user_key", "namespace", "routing_key"],
    )

    def count_events(gauge: Gauge, silenced: bool):
        async def counter(_) -> None:
            async with sessionmaker() as session, session.begin():
                for listener, count in (
                    await session.execute(
                        select(Listener, func.count(Event.pk))
                        .outerjoin(
                            Event,
                            (Listener.pk == Event.listener_fk)
                            & (Event.silenced == silenced),
                        )
                        .group_by(Listener.pk)
                    )
                ).all():
                    gauge.labels(
                        owner=listener.owner,
                        user_key=listener.user_key,
                        namespace=listener.namespace,
                        routing_key=listener.routing_key,
                    ).set(count)

        return counter

    instrumentator.add(count_events(silenced_events, silenced=True))
    instrumentator.add(count_events(active_events, silenced=False))


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
