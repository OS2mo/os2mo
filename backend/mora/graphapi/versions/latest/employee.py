# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from ....mapping import RequestType
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .types import EmployeeType
from .types import EmployeeUpdateResponseType
from mora import common
from mora import lora
from mora import mapping
from mora import util
from mora.service import handlers
from mora.service.employee import EmployeeRequestHandler
from mora.triggers import Trigger


async def create(input: EmployeeCreate) -> EmployeeType:
    input_dict = input.to_handler_dict()

    # Copied service-logic
    handler = await EmployeeRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return EmployeeType(uuid=UUID(uuid))


async def terminate(termination: EmployeeTerminate) -> EmployeeType:
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

    if not util.get_args_flag("triggerless"):
        await Trigger.run(trigger_dict)

    for handler in request_handlers:
        await handler.submit()

    result = uuid

    trigger_dict[Trigger.EVENT_TYPE] = mapping.EventType.ON_AFTER
    trigger_dict[Trigger.RESULT] = result

    if not util.get_args_flag("triggerless"):
        await Trigger.run(trigger_dict)

    # Write a noop entry to the user, to be used for the history
    await common.add_history_entry(c.bruger, uuid, "Afslut medarbejder")

    return EmployeeType(uuid=UUID(result))


async def update(employee_update: EmployeeUpdate) -> EmployeeUpdateResponseType:
    request_handler_dict = employee_update.to_handler_dict()
    request_handler = await EmployeeRequestHandler.construct(
        request_handler_dict, RequestType.EDIT
    )

    new_uuid = await request_handler.submit()

    return EmployeeUpdateResponseType(uuid=UUID(new_uuid))


# async def update(employee_update: EmployeeUpdate) -> EmployeeUpdateResponseType:
#     if employee_update.no_values():
#         return EmployeeUpdateResponseType(uuid=employee_update.uuid)

#     result = await handle_requests(
#         employee_update.get_legacy_dict(), mapping.RequestType.EDIT
#     )

#     # Based on the logic at: backend/mora/lora.py:159
#     # If there is no data changed, it looks like we wont get a UUID  back.
#     updated_uuid = UUID(result) if result else employee_update.uuid

#     return EmployeeUpdateResponseType(uuid=updated_uuid)


# Helper methods
def _is_update_changeset_empty(employee_update: EmployeeUpdate) -> bool:
    if employee_update.to_date:
        return False

    if employee_update.name or employee_update.given_name or employee_update.surname:
        return False

    if (
        employee_update.nickname
        or employee_update.nickname_given_name
        or employee_update.nickname_surname
    ):
        return False

    if employee_update.seniority or employee_update.cpr_no:
        return False

    return True
