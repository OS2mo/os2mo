# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from sqlalchemy import UUID as SUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import Base


class Audit(Base):
    __tablename__ = "audit"

    id: Mapped[UUID] = mapped_column(SUUID, primary_key=True)
    client: Mapped[str] = mapped_column(String, nullable=False)
