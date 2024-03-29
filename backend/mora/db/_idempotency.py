# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from ._common import Base


class Idempotency(Base):
    __tablename__ = "idempotency"

    # Token can be generated via uuid3 or uuid5 from application specific data
    token: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )
    time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), index=True
    )
    # Not actually needed for idempotency checking, but could be useful for the future
    actor: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    # UUID of the created entity
    result: Mapped[UUID] = mapped_column(Uuid, nullable=False)
