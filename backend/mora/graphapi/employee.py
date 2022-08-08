#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
from typing import Optional

from ramodels.mo.employee import EmployeeTerminate
from ramodels.mo.employee import EmployeeTerminate as RaModelEmployeeTerminate
from ramodels.mo.employee import OpenValidity

from mora import common
from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.graphapi.models import EmployeeTermination
from mora.graphapi.types import EmployeeType
from mora.service import handlers
from mora.triggers import Trigger
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY


async def terminate_employee(e_termination: EmployeeTermination) -> EmployeeType:
    """Termination handler for employee."""
    uuid = str(e_termination.uuid)
    ramodel = RaModelEmployeeTerminate(
        validity=OpenValidity(
            from_date=e_termination.from_date, to_date=e_termination.to_date
        )
    )

    date = _get_valid_to(ramodel.validity.to_date.date())
    request_dict = _create_request_dict_from_e_terminate(ramodel)

    c = lora.Connector(effective_date=date, virkningtil="infinity")

    request_handlers = [
        await handlers.get_handler_for_function(obj).construct(
            {
                "uuid": objid,
                "vacate": util.checked_get(request_dict, "vacate", False),
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
        Trigger.REQUEST: request_dict,
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

    return EmployeeType(uuid=result)


def _get_valid_to(to_date: Optional[datetime.date]) -> datetime.datetime:
    if not to_date:
        return POSITIVE_INFINITY

    dt = datetime.datetime.combine(to_date, datetime.datetime.min.time())
    if dt.time() != datetime.time.min:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            "{!r} is not at midnight!".format(dt.isoformat()),
        )

    return _apply_default_tz(dt + ONE_DAY)


def _apply_default_tz(dt: datetime.datetime) -> datetime.datetime:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=util.DEFAULT_TIMEZONE)
    else:
        dt = dt.astimezone(util.DEFAULT_TIMEZONE)

    return dt


def _create_request_dict_from_e_terminate(
    employee_terminate: EmployeeTerminate,
) -> dict:
    request_dict = employee_terminate.dict(by_alias=True)
    if employee_terminate.validity.from_date:
        request_dict[mapping.VALIDITY][
            mapping.FROM
        ] = employee_terminate.validity.from_date.strftime("%Y-%m-%d")
    else:
        del request_dict[mapping.VALIDITY][mapping.FROM]

    if employee_terminate.validity.to_date:
        request_dict[mapping.VALIDITY][
            mapping.TO
        ] = employee_terminate.validity.to_date.strftime("%Y-%m-%d")
    else:
        del request_dict[mapping.VALIDITY][mapping.TO]

    return request_dict
