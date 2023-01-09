# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from ....mapping import RequestType
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .types import UUIDReturn
from mora import common
from mora import lora
from mora import mapping
from mora import util
from mora.service import handlers
from mora.service.employee import EmployeeRequestHandler
from mora.triggers import Trigger


async def create(input: EmployeeCreate) -> UUIDReturn:
    input_dict = input.to_handler_dict()

    # Copied service-logic
    handler = await EmployeeRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUIDReturn(uuid=UUID(uuid))


async def terminate(termination: EmployeeTerminate) -> UUIDReturn:
    # Create request dict, legacy, from data model
    request = {mapping.VALIDITY: {mapping.TO: termination.to_date.date().isoformat()}}
    if termination.from_date:
        request[mapping.VALIDITY][
            mapping.FROM
        ] = termination.from_date.date().isoformat()

    # Current logic - copied from os2mo.backend.service
    uuid = str(termination.uuid)
    date = util.get_valid_to(request)

    c = lora.Connector(effective_date=date, virkningtil="infinity")

    request_handlers = [
        await handlers.get_handler_for_function(obj).construct(
            {
                "uuid": objid,
                "vacate": util.checked_get(request, "vacate", False),
                "validity": {
                    "to": util.to_iso_date(
                        # we also want to handle _future_ relations
                        max(date, min(map(util.get_effect_from, util.get_states(obj)))),
                        is_end=True,
                    ),
                },
            },
            mapping.RequestType.TERMINATE,
        )
        for objid, obj in await c.organisationfunktion.get_all(
            tilknyttedebrugere=uuid,
            gyldighed="Aktiv",
        )
    ]

    trigger_dict = {
        Trigger.ROLE_TYPE: mapping.EMPLOYEE,
        Trigger.EVENT_TYPE: mapping.EventType.ON_BEFORE,
        Trigger.REQUEST: request,
        Trigger.REQUEST_TYPE: mapping.RequestType.TERMINATE,
        Trigger.EMPLOYEE_UUID: uuid,
        Trigger.UUID: uuid,
    }

    await Trigger.run(trigger_dict)

    for handler in request_handlers:
        await handler.submit()

    result = uuid

    trigger_dict[Trigger.EVENT_TYPE] = mapping.EventType.ON_AFTER
    trigger_dict[Trigger.RESULT] = result

    await Trigger.run(trigger_dict)

    # Write a noop entry to the user, to be used for the history
    await common.add_history_entry(c.bruger, uuid, "Afslut medarbejder")

    return UUIDReturn(uuid=UUID(result))


async def update(employee_update: EmployeeUpdate) -> UUIDReturn:
    request_handler = await EmployeeRequestHandler.construct(
        employee_update.to_handler_dict(), RequestType.EDIT
    )
    _ = await request_handler.submit()
    return UUIDReturn(uuid=employee_update.uuid)
