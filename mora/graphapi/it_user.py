# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.config import Settings
from mora.service.itsystem import ItsystemRequestHandler

from .models import ITUserCreate
from .models import ITUserTerminate
from .models import ITUserUpdate


async def create_ituser(input: ITUserCreate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE, settings
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_ituser(input: ITUserUpdate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.IT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ItsystemRequestHandler.construct(
        req, mapping.RequestType.EDIT, settings
    )
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_ituser(input: ITUserTerminate, settings: Settings) -> UUID:
    await _validate_no_active_rolebindings(input)

    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE, settings
    )
    await request.submit()

    return input.uuid


async def _validate_no_active_rolebindings(input: ITUserTerminate) -> None:
    if input.from_date:
        date = input.get_terminate_effect_from_date()
    else:
        date = input.get_terminate_effect_to_date()

    ituser_uuid = str(input.uuid)
    c = lora.Connector(effective_date=util.to_iso_date(date))
    rolebindings = set(
        await c.organisationfunktion.load_uuids(
            tilknyttedefunktioner=ituser_uuid,
            gyldighed="Aktiv",
            funktionsnavn=mapping.ROLEBINDING_KEY,
        )
    )

    if rolebindings:
        exceptions.ErrorCodes.V_TERMINATE_ITUSER_WITH_ROLEBINDINGS(
            rolebinding_uuids=sorted(rolebindings),
        )
