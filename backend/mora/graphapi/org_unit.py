#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL org-unit related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import logging
from typing import cast
from uuid import UUID

from strawberry.dataloader import DataLoader

from mora import exceptions
from mora import mapping
from mora import util
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.inputs import OrganizationUnitTerminateInput
from mora.graphapi.schema import Response
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.orgunit import terminate_org_unit_validation


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


async def terminate_org_unit(unit: OrganizationUnitTerminateInput) -> bool:
    # Create lora payload
    # effect = OrgUnitRequestHandler.get_virkning_for_terminate(request)

    # Setup terminate dict
    terminate_dict: dict = {
        mapping.UUID: str(unit.uuid),
        mapping.VALIDITY: {mapping.FROM: unit.from_date, mapping.TO: unit.to_date},
    }

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
        await terminate_org_unit_validation(
            terminate_dict[mapping.UUID], terminate_dict
        )
    except Exception as e:
        logger.exception("ERROR validating termination request.")
        raise e

    # Handle the unit UUID
    # uuid = util.get_uuid(terminate_dict)

    # Create payload to LoRa
    obj_path = ("tilstande", "organisationenhedgyldighed")
    effect = OrgUnitRequestHandler.get_virkning_for_terminate(terminate_dict)
    val_inactive = {"gyldighed": "Inaktiv", "virkning": effect}

    lora_payload = util.set_obj_value(dict(), obj_path, [val_inactive])
    lora_payload["note"] = "Afslut enhed"

    # TODO: Finish the termiante logic
    # # Conn to LoRa
    # lora_conn = lora.Connector()
    # result = await lora_conn.organisationenhed.update(lora_payload, uuid)
    return True
