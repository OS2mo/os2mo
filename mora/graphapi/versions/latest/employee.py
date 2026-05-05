# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import common
from mora import lora
from mora import mapping
from mora import util
from mora.service import handlers
from mora.service.employee import EmployeeRequestHandler
from mora.triggers import Trigger

from ....mapping import RequestType
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate


async def create_employee(input: EmployeeCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await EmployeeRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()
    # coverage: pause
    return UUID(uuid)
    # coverage: unpause


async def update_employee(input: EmployeeUpdate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.EMPLOYEE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await EmployeeRequestHandler.construct(req, RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_employee(termination: EmployeeTerminate) -> UUID:
    # Create request dict, legacy, from data model
    request = {mapping.VALIDITY: {mapping.TO: termination.to_date.date().isoformat()}}
    if termination.from_date:  # pragma: no cover
        request[mapping.VALIDITY][mapping.FROM] = (
            termination.from_date.date().isoformat()
        )

    uuid = str(termination.uuid)
    date = util.get_valid_to(request)

    c = lora.Connector(effective_date=date, virkningtil="infinity")

    request_handlers = [
        await handlers.get_handler_for_function(obj).construct(
            {
                "uuid": objid,
                "vacate": termination.vacate,
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
    # coverage: pause
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

    return UUID(result)
    # coverage: unpause
