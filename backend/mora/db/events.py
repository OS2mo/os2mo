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

    __table_args__ = (UniqueConstraint('user_key', 'owner', 'namespace', "routing_key", name='uq_user_key_owner_namespace_routing_key'),)


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

    __table_args__ = (UniqueConstraint('listener_fk', 'subject', 'priority', name='uq_listener_subject_priority'),)


async def add_events(session, namespace: str, routing_key: str, subject: str, priority: int = 10):
    matching_listeners = select(Listener.pk).where(
        Listener.namespace == namespace,
        Listener.routing_key == routing_key,
    )

    stmt = insert(Event).from_select(
        ["pk", "listener_fk", "subject", "priority", "last_tried", "silenced"],
        select(
            text("uuid_generate_v4()"),
            Listener.pk,
            literal(subject),
            literal(priority),
            # last_tried. We subtract 5 minutes, so it is sent faster.
            text("now() - interval '5 minutes'"),
            text("false"),  # silenced
        ).where(Listener.pk.in_(matching_listeners)),
    ).on_conflict_do_update(
        index_elements=["listener_fk", "subject", "priority"],
        # When we violate the unique constraint, update `last_tried`.
        # This ensures that clients won't miss an event in the case where
        # a new event arrives while the client is already processing an
        # event for the same subject.
        set_={"last_tried": text("now()")},
    )

    await session.execute(stmt)
