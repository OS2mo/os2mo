# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import Base
from ._common import PgSnapshot


class AMQPSubsystem(Base):
    __tablename__ = "amqp_subsystem"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Wall-clock time of the previous event generator run.
    # Detect validity boundaries that have elapsed since last event generation.
    last_validity_run: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # MVCC snapshot as of the previous event generator run.
    # Detect registrations that have become visible since last event generation.
    #
    # Initially we used last_validity_run/wall-clock (then "last_run") for both
    # validities and registrations. However, this implementation has a subtle
    # bug: if the event generator is running while another transaction (not
    # committed, therefore invisible to the event generator) is writing, that
    # transaction/registration could be skipped completely by the event system.
    #
    # Technically, this bug is still present for validities, _but_ that can
    # only happen when it goes into effect "now" which means an event would
    # still be emitted for the registration. As we just guarentee at-least-once
    # delivery, the system as a whole does not have a bug.
    last_registration_snapshot: Mapped[str] = mapped_column(PgSnapshot())

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"AMQPSubsystem(id={self.id!r}, "
            f"last_validity_run={self.last_validity_run!r}, "
            f"last_registration_snapshot={self.last_registration_snapshot!r})"
        )
