#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL org-unit related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
import logging
from typing import cast
from uuid import UUID

from strawberry.dataloader import DataLoader

from mora import common
from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.inputs import OrganizationUnitTerminateInput
from mora.graphapi.schema import Response
from mora.graphapi.types import OrganizationUnit
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.orgunit import terminate_org_unit_validation
from mora.triggers import Trigger
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


async def load_org_unit(uuid: UUID) -> Response:
    """Call the org_unit_loader on the given UUID.

    Args:
        uuid: The UUID to load from LoRa.

    Returns:
        The return from LoRa.
    """
    loaders = await get_loaders()
    org_unit_loader = cast(DataLoader, loaders["org_unit_loader"])
    return await org_unit_loader.load(uuid)


async def trigger_org_unit_refresh(uuid: UUID) -> dict[str, str]:
    """Trigger external integration for a given org unit UUID.

    Args:
        uuid: UUID of the org unit to trigger refresh for.

    Returns:
        The submit result.
    """
    response = await load_org_unit(uuid)
    if not response.objects:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=str(uuid))

    request = {mapping.UUID: str(uuid)}
    handler = await OrgUnitRequestHandler.construct(
        request, mapping.RequestType.REFRESH
    )
    result = await handler.submit()
    return result


async def terminate_org_unit(unit: OrganizationUnitTerminateInput) -> OrganizationUnit:
    # Create lora payload
    # effect = OrgUnitRequestHandler.get_virkning_for_terminate(request)
    effect = _get_terminate_effect(unit)

    # Setup terminate dict
    terminate_dict: dict = {
        mapping.UUID: str(unit.uuid),
        mapping.VALIDITY: {mapping.FROM: unit.from_date, mapping.TO: unit.to_date},
    }

    # Verify the unit UUID
    uuid = util.get_uuid(terminate_dict)

    # Handle dates
    if unit.from_date:
        terminate_dict[mapping.VALIDITY][mapping.FROM] = unit.from_date.strftime(
            "%Y-%m-%d"
        )
    else:
        del terminate_dict[mapping.VALIDITY][mapping.FROM]

    if unit.to_date:
        terminate_dict[mapping.VALIDITY][mapping.TO] = unit.to_date.strftime("%Y-%m-%d")
    else:
        del terminate_dict[mapping.VALIDITY][mapping.TO]

    # OBS: This validation method ALSO instantiates a lora.Connector().. but with an
    # "effective_date" arg.. not sure what this does yet, but i will let it be for now.
    # would be cool if we only had to create 1 connector
    # ALSO: would be nice to only need a terminate dict since the UUID is added to it..
    # or use proper arguments like:
    # `terminate_org_unit_validation(uuid: str, from: datetime.date, to: datetime.date)`
    try:
        await terminate_org_unit_validation(uuid, terminate_dict)
    except Exception as e:
        logger.exception("ERROR validating termination request.")
        raise e

    # Create payload to LoRa
    obj_path = ("tilstande", "organisationenhedgyldighed")
    effect = OrgUnitRequestHandler.get_virkning_for_terminate(terminate_dict)
    val_inactive = {"gyldighed": "Inaktiv", "virkning": effect}

    lora_payload = util.set_obj_value(dict(), obj_path, [val_inactive])
    lora_payload["note"] = "Afslut enhed"

    # TODO: Finish the termiante logic

    trigger_dict = _create_trigger_dict_from_org_unit_input(unit)

    # ON_BEFORE
    # trigger_results_before = None
    if not util.get_args_flag("triggerless"):
        _ = await Trigger.run(trigger_dict)

    # Do LoRa update
    lora_conn = lora.Connector()
    lora_result = await lora_conn.organisationenhed.update(lora_payload, uuid)
    trigger_dict[Trigger.RESULT] = lora_result

    # ON_AFTER
    trigger_dict.update(
        {
            Trigger.RESULT: lora_result,
            Trigger.EVENT_TYPE: mapping.EventType.ON_AFTER,
        }
    )
    # trigger_results_after = None
    if not util.get_args_flag("triggerless"):
        _ = await Trigger.run(trigger_dict)

    # Return the unit as the final thing
    return OrganizationUnit(uuid=trigger_dict.get(Trigger.RESULT))


def _get_terminate_effect(unit: OrganizationUnitTerminateInput) -> dict:
    if unit.from_date and unit.to_date:
        return common._create_virkning(
            _get_valid_from(unit.from_date),
            _get_valid_to(unit.to_date),
        )

    if not unit.from_date and unit.to_date:
        return common._create_virkning(_get_valid_to(unit.to_date), "infinity")

    exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
        # key="Validity must be set with either 'to' or both 'from' " "and 'to'",
        # NOTE: This is the OG way.. the one below is my try to remake it in case we
        # need them for tests
        # obj=request,
        # obj={
        #     "validity": {
        #         "from": unit.from_date.isoformat() if unit.from_date else None,
        #         "to": unit.to_date.isoformat() if unit.to_date else None
        #     }
        # },
        key="Organization Unit must be set with either 'to' or both 'from' " "and 'to'",
        unit={
            "from": unit.from_date.isoformat() if unit.from_date else None,
            "to": unit.to_date.isoformat() if unit.to_date else None,
        },
    )


def _get_valid_from(from_date: datetime.date) -> datetime.datetime:
    if not from_date:
        exceptions.ErrorCodes.V_MISSING_START_DATE()

    dt = datetime.datetime.combine(from_date.today(), datetime.datetime.min.time())
    if dt.time() != datetime.time.min:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            "{!r} is not at midnight!".format(dt.isoformat()),
        )

    return dt


def _get_valid_to(to_date: datetime.date) -> datetime.datetime:
    if not to_date:
        return POSITIVE_INFINITY

    dt = datetime.datetime.combine(to_date.today(), datetime.datetime.min.time())
    if dt.time() != datetime.time.min:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            "{!r} is not at midnight!".format(dt.isoformat()),
        )

    return dt + ONE_DAY


def _create_trigger_dict_from_org_unit_input(
    unit: OrganizationUnitTerminateInput,
) -> dict:
    uuid_str = str(unit.uuid)

    # create trigger dict request
    trigger_request = {
        mapping.TYPE: mapping.ORG_UNIT,
        mapping.UUID: uuid_str,
        mapping.VALIDITY: {},
    }

    if unit.from_date:
        trigger_request[mapping.VALIDITY][mapping.FROM] = unit.from_date.isoformat()

    if unit.to_date:
        trigger_request[mapping.VALIDITY][mapping.TO] = unit.to_date.isoformat()

    # Create the return dict
    trigger_dict = {
        Trigger.REQUEST_TYPE: mapping.RequestType.TERMINATE,
        Trigger.REQUEST: trigger_request,
        Trigger.ROLE_TYPE: mapping.ORG_UNIT,
        Trigger.ORG_UNIT_UUID: uuid_str,
        Trigger.EVENT_TYPE: mapping.EventType.ON_BEFORE,
        # Trigger.EVENT_TYPE: mapping.EventType.ON_AFTER,
        Trigger.UUID: uuid_str,
        Trigger.RESULT: None,
    }

    return trigger_dict
