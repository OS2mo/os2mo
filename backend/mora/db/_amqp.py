# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import Base


class AMQPSubsystem(Base):
    __tablename__ = "amqp_subsystem"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_run: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:  # pragma: no cover
        return f"AMQPSubsystem(id={self.id!r}, last_run={self.last_run!r})"
