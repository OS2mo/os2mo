# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Sequence
from enum import Enum
from typing import Any
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from mora.auth.middleware import get_authenticated_user
from mora.config import Settings
from mora.db import AccessLogOperation
from mora.db import AccessLogRead
from mora.db import AsyncSession


@strawberry.enum
class AccessLogModel(Enum):
    ACCESS_LOG = "AccessLog"
    ACTOR = "Actor"
    PERSON = "Bruger"
    CPR_LOOKUP = "CPRPerson"
    FACET = "Facet"
    FILE = "File"
    IT_SYSTEM = "ItSystem"
    CLASS = "Klasse"
    ORGANISATION = strawberry.enum_value(
        "Organisation",
        deprecation_reason="The root organisation concept will be removed in a future version of OS2mo.",
    )
    ORGANISATION_UNIT = "OrganisationEnhed"
    ORGANISATION_FUNCTION = "OrganisationFunktion"
    REGISTRATION = "Registration"

    @classmethod
    def from_lora(cls, class_name: str) -> "AccessLogModel":
        """Get the model of a LoRa class.

        LoRa class names are case-insensitive, and are not consistently cased
        by their callers, e.g. both "ItSystem" and "itsystem" are used.
        """
        return one(model for model in cls if model.value.lower() == class_name.lower())


def access_log(
    session: AsyncSession,
    settings: Settings,
    operation: str,
    model: AccessLogModel,
    arguments: dict[str, Any],
    uuids: Sequence[UUID],
) -> None:
    """Insert an entry into the access log.

    Args:
        session: SQLAlchemy sync or async session within an active transaction.
        settings: Settings deciding whether, and for whom, to log.
        operation: Name of the current operation.
        model: Model of the data entry being accessed.
        arguments: Arguments provided to operation.
        uuids: UUIDs read by the operation.
    """
    if not settings.access_log_enable:
        return
    if get_authenticated_user() in settings.access_log_no_log_uuids:
        return

    operation = AccessLogOperation(
        actor=get_authenticated_user(),
        model=model.value,
        operation=operation,
        arguments=jsonable_encoder(arguments),
    )
    uuids = [AccessLogRead(operation=operation, uuid=uuid) for uuid in uuids]
    session.add(operation)
    session.add_all(uuids)
