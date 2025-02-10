# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org-unit related helper functions."""

import logging
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.service.orgunit import OrgUnitRequestHandler
from mora.service.validation import validator

from ...version import Version
from .inputs import OrganisationUnitCreateInput
from .inputs import OrganisationUnitUpdateInput
from .inputs import strip_none
from .models import OrganisationUnitTerminate

logger = logging.getLogger(__name__)


async def create_org_unit(input: OrganisationUnitCreateInput) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await OrgUnitRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_org_unit(version: Version, input: OrganisationUnitUpdateInput) -> UUID:
    """Updating an organisation unit."""
    handler_dict = input.to_handler_dict()
    if version <= Version.VERSION_21:
        handler_dict = strip_none(handler_dict)

    input_dict = jsonable_encoder(handler_dict)

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
    try:
        await terminate_org_unit_validation(input)
    except Exception as e:
        logger.exception("ERROR validating termination request.")
        raise e

    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await OrgUnitRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
