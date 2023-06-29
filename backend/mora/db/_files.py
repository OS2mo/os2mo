# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from ._common import Base


class FileToken(Base):
    __tablename__ = "file_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
