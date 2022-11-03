# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org-unit related helper functions."""
import logging
from typing import cast
from uuid import UUID

from strawberry.dataloader import DataLoader

from .dataloaders import get_loaders
from .models import MoraTriggerRequest
from .models import OrganisationUnitCreate
from .models import OrganisationUnitTerminate
from .models import OrganisationUnitUpdate
from .models import OrgUnitTrigger
from .models import Validity
from .schema import Response
from .types import OrganisationUnitType
from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.validation import validator
from mora.triggers import Trigger

logger = logging.getLogger(__name__)


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


async def terminate_org_unit_validation(
    ou_terminate: OrganisationUnitTerminate,
) -> None:
    uuid_str = str(ou_terminate.uuid)

    # Get & verify basic date
    if ou_terminate.from_date and ou_terminate.to_date:
        date = ou_terminate.get_terminate_effect_from_date()
    else:
        date = ou_terminate.get_terminate_effect_to_date()

    # Verify date against OrgUnit range
    await validator.is_date_range_in_org_unit_range(
        {"uuid": uuid_str},
        date - util.MINIMAL_INTERVAL,
        date,
    )

    # Find children, roles and addresses, and verify constraints

    # Find & verify there is no children
    c = lora.Connector(effective_date=util.to_iso_date(date))
    children = set(
        await c.organisationenhed.load_uuids(
            overordnet=uuid_str,
            gyldighed="Aktiv",
        )
    )

    roles = set(
        await c.organisationfunktion.load_uuids(
            tilknyttedeenheder=uuid_str,
            gyldighed="Aktiv",
        )
    )

    addresses = set(
        await c.organisationfunktion.load_uuids(
            tilknyttedeenheder=uuid_str,
            funktionsnavn=mapping.ADDRESS_KEY,
            gyldighed="Aktiv",
        )
    )

    active_roles = roles - addresses
    role_counts = set()
    if active_roles:
        role_counts = {
            mapping.ORG_FUNK_EGENSKABER_FIELD.get(obj)[0]["funktionsnavn"]
            for objid, obj in await c.organisationfunktion.get_all_by_uuid(
                uuids=active_roles
            )
        }

    if children and role_counts:
        exceptions.ErrorCodes.V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES(
            child_count=len(children),
            roles=", ".join(sorted(role_counts)),
        )
    elif children:
        exceptions.ErrorCodes.V_TERMINATE_UNIT_WITH_CHILDREN(
            child_count=len(children),
        )
    elif role_counts:
        exceptions.ErrorCodes.V_TERMINATE_UNIT_WITH_ROLES(
            roles=", ".join(sorted(role_counts)),
        )


async def terminate_org_unit(
    ou_terminate: OrganisationUnitTerminate,
) -> OrganisationUnitType:
    try:
        await terminate_org_unit_validation(ou_terminate)
    except Exception as e:
        logger.exception("ERROR validating termination request.")
        raise e

    # Create payload to LoRa
    org_unit_trigger = OrgUnitTrigger(
        employee_id=None,
        org_unit_uuid=ou_terminate.uuid,
        request_type=mapping.RequestType.TERMINATE,
        request=MoraTriggerRequest(
            type=mapping.ORG_UNIT,
            uuid=ou_terminate.uuid,
            validity=Validity(
                from_date=ou_terminate.from_date,
                to_date=ou_terminate.to_date,
            ),
        ),
        role_type=mapping.ORG_UNIT,
        event_type=mapping.EventType.ON_BEFORE,
        uuid=ou_terminate.uuid,
    )

    trigger_dict = org_unit_trigger.to_trigger_dict()

    # ON_BEFORE
    _ = await Trigger.run(trigger_dict)

    # Do LoRa update
    lora_conn = lora.Connector()
    lora_result = await lora_conn.organisationenhed.update(
        ou_terminate.get_lora_payload(), ou_terminate.uuid
    )

    # ON_AFTER
    trigger_dict.update(
        {
            Trigger.RESULT: lora_result,
            Trigger.EVENT_TYPE: mapping.EventType.ON_AFTER,
        }
    )

    # ON_AFTER
    _ = await Trigger.run(trigger_dict)

    # Return the unit as the final thing
    return OrganisationUnitType(uuid=lora_result)


async def create_org_unit(input: OrganisationUnitCreate) -> OrganisationUnitType:
    input_dict = input.to_handler_dict()

    handler = await OrgUnitRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return OrganisationUnitType(uuid=UUID(uuid))


async def update_org_unit(input: OrganisationUnitUpdate) -> OrganisationUnitType:
    """Updating an organisation unit."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ORG_UNIT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await OrgUnitRequestHandler.construct(req, mapping.RequestType.EDIT)

    uuid = await request.submit()

    return OrganisationUnitType(uuid=UUID(uuid))
