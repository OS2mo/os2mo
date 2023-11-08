# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org-unit related helper functions."""
import logging
from uuid import UUID

from .models import MoraTriggerRequest
from .models import OrganisationUnitCreate
from .models import OrganisationUnitTerminate
from .models import OrganisationUnitUpdate
from .models import OrgUnitTrigger
from .models import Validity
from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.validation import validator
from mora.triggers import Trigger

logger = logging.getLogger(__name__)


async def create_org_unit(input: OrganisationUnitCreate) -> UUID:
    input_dict = input.to_handler_dict()

    request = await OrgUnitRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_org_unit(input: OrganisationUnitUpdate) -> UUID:
    """Updating an organisation unit."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ORG_UNIT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await OrgUnitRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


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

    # Find children and roles and verify constraints

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

    active_roles = roles
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
    input: OrganisationUnitTerminate,
) -> UUID:
    ou_terminate = input
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
        ou_terminate.get_lora_payload(), str(ou_terminate.uuid)
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
    return UUID(lora_result)
