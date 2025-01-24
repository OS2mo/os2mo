# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import Base


class AMQPSubsystem(Base):
    __tablename__ = "amqp_subsystem"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_run: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"AMQPSubsystem(id={self.id!r}, last_run={self.last_run!r})"


class Listeners(Base):
    __tablename__ = "amqp_listener"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    owner: Mapped[UUID] = mapped_column()
    routing_key: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"Listeners(uuid={self.uuid!r}, owner={self.owner!r}, routing_key={self.routing_key!r})"


class Events(Base):
    __tablename__ = "amqp_event"

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    listener: Mapped[UUID] = mapped_column(ForeignKey("amqp_listener.uuid"), index=True)
    payload: Mapped[JSON] = mapped_column(type_=JSON)

    # status: Mapped[enum] = mapped_column() #Paused, Active
    def __repr__(self) -> str:
        return f"Events(uuid={self.uuid!r}, listener={self.listener!r}, payload={self.payload!r})"
