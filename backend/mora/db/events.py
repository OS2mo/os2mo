# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID
from typing import Literal

from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM
from ._common import Base
from ._common import metadata


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

    # __table_args__ = (UniqueConstraint('listener_fk', 'identifier', 'state', name='uq_listener_identifier_state'),)
