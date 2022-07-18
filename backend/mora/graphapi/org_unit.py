#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL org-unit related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import cast
from uuid import UUID

from strawberry.dataloader import DataLoader

from mora import exceptions
from mora import mapping
from mora import lora
from mora import util
from mora.graphapi.dataloaders import get_loaders
from mora.graphapi.schema import Response
from mora.service.orgunit import OrgUnitRequestHandler

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

async def terminate_org_unit(uuid: UUID) -> bool:
    # Create lora payload
    # virkning = OrgUnitRequestHandler.get_virkning_for_terminate(request)
    obj_path = ("tilstande", "organisationenhedgyldighed")
    val_inactive = {
        "gyldighed": "Inaktiv",
        "virkning": virkning,
    }

    payload = util.set_obj_value(dict(), obj_path, [val_inactive])
    payload["note"] = "Afslut enhed"

    payload = None


    # Connect and update
    c = lora.Connector()
    result = await c.organisationenhed.update(payload, uuid)
