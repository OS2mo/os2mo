# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy import text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from ._common import Base

# Well-known "magic" UUID of the bootstrap "policyadmin" policy. It is inserted
# by a migration and protected from deletion via the `policy_delete` mutator.
POLICYADMIN_UUID = UUID("ded1ca7e-9bac-5eed-706f-6c61646d696e")


class Policy(Base):
    __tablename__ = "policy"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str]
    description: Mapped[str | None]
    # Validity is modelled as two plain timestamps. A null `end` means the policy
    # is open-ended. This is not bitemporal like the LoRa entities.
    start: Mapped[datetime]
    end: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))

    actors: Mapped[list["PolicyActor"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


class PolicyActor(Base):
    __tablename__ = "policy_actor"

    pk: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    # The kind of actor attribute to match on: "uuid", "username" or "role".
    kind: Mapped[str]
    # The value the attribute must equal (a uuid string, username or role name).
    value: Mapped[str]

    policy_fk: Mapped[UUID] = mapped_column(ForeignKey("policy.id"))
    policy: Mapped[Policy] = relationship(back_populates="actors")
