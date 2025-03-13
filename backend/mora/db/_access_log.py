# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Uuid
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ._common import Base


class AccessLogOperation(Base):
    __tablename__ = "access_log_operation"

    # TODO: Use gen_random_uuid after Postgres 13+
    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuid_generate_v4()")
    )
    time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), index=True
    )
    actor: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    operation: Mapped[str] = mapped_column(String(255), nullable=False)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    uuids: Mapped[list["AccessLogRead"]] = relationship(back_populates="operation")


class AccessLogRead(Base):
    __tablename__ = "access_log_read"

    # TODO: Use gen_random_uuid after Postgres 13+
    id: Mapped[UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuid_generate_v4()")
    )

    operation_id: Mapped[UUID] = mapped_column(ForeignKey("access_log_operation.id"))
    operation: Mapped["AccessLogOperation"] = relationship(back_populates="uuids")

    uuid: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
