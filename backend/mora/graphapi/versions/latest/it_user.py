# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.service.itsystem import ItsystemRequestHandler

from .models import ITUserCreate
from .models import ITUserTerminate
from .models import ITUserUpdate

logger = logging.getLogger(__name__)


async def create_ituser(input: ITUserCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_ituser(input: ITUserUpdate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.IT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ItsystemRequestHandler.construct(req, mapping.RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_ituser_validation(
    ituser_terminate: ITUserTerminate,
) -> None:
    uuid_str = str(ituser_terminate.uuid)

    # Get & verify basic date
    if ituser_terminate.from_date and ituser_terminate.to_date:
        date = ituser_terminate.get_terminate_effect_from_date()
    else:
        date = ituser_terminate.get_terminate_effect_to_date()

    # coverage: pause
    c = lora.Connector(effective_date=util.to_iso_date(date))
    roles = set(
        await c.organisationfunktion.load_uuids(
            tilknyttedefunktioner=uuid_str,
            gyldighed="Aktiv",
        )
    )

    active_roles = roles
    role_counts = set()
    if active_roles:
        role_counts = {
            mapping.ORG_FUNK_EGENSKABER_FIELD.get(obj)[0]["funktionsnavn"]
            for objid, obj in await c.organisationfunktion.get_all_by_uuid(
                uuids=active_roles
            )
        }

    if role_counts:
        exceptions.ErrorCodes.V_TERMINATE_ITUSER_WITH_ROLEBINDINGS(
            roles=", ".join(sorted(role_counts)),
        )
    # coverage: unpause


async def terminate_ituser(input: ITUserTerminate) -> UUID:  # pragma: no cover
    try:
        await terminate_ituser_validation(input)
    except Exception as e:  # pragma: no cover
        logger.exception("ERROR validating termination request.")
        raise e

    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
