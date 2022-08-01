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
from typing import Optional
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
from mora.service.validation import validator
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


async def terminate_org_unit_validation(
    unit_uuid: UUID,
    from_date: Optional[datetime.datetime],
    to_date: Optional[datetime.datetime],
) -> None:
    uuid_str = str(unit_uuid)

    # Verify date
    # date = (
    #     _get_valid_from(from_date) if from_date and to_date else _get_valid_to(to_date)
    # )

    # if not to_date:
    #     date = POSITIVE_INFINITY
    # else:
    #     if to_date.time() != datetime.time.min:
    #         raise exceptions.ErrorCodes.E_INVALID_INPUT(
    #             "{!r} is not at midnight!".format(dt.isoformat()),
    #         )
    #
    # date = to_date

    if from_date and to_date:
        if not from_date or not isinstance(from_date, datetime.date):
            raise exceptions.ErrorCodes.V_MISSING_START_DATE()

        date = from_date
    else:
        if to_date and to_date.time() != datetime.time.min:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                "{!r} is not at midnight!".format(to_date.isoformat()),
            )

        date = to_date if to_date else POSITIVE_INFINITY

    c = lora.Connector(effective_date=util.to_iso_date(date))
    await validator.is_date_range_in_org_unit_range(
        {"uuid": uuid_str},
        date - util.MINIMAL_INTERVAL,
        date,
    )

    # Find children, roles and addresses, and verify constraints
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
        role_counts = set(
            mapping.ORG_FUNK_EGENSKABER_FIELD.get(obj)[0]["funktionsnavn"]
            for objid, obj in await c.organisationfunktion.get_all_by_uuid(
                uuids=active_roles
            )
        )

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


async def terminate_org_unit(unit: OrganizationUnitTerminateInput) -> OrganizationUnit:
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
        await terminate_org_unit_validation(unit.uuid, unit.from_date, unit.to_date)
    except Exception as e:
        logger.exception("ERROR validating termination request.")
        raise e

    # Create payload to LoRa
    obj_path = ("tilstande", "organisationenhedgyldighed")
    effect = _get_terminate_effect(unit)
    val_inactive = {"gyldighed": "Inaktiv", "virkning": effect}

    lora_payload = util.set_obj_value(dict(), obj_path, [val_inactive])
    lora_payload["note"] = "Afslut enhed"

    # TODO: Finish the termiante logic

    trigger_dict = _create_trigger_dict_from_org_unit_input(unit)

    # ON_BEFORE
    # if not util.get_args_flag("triggerless"):
    if not unit.trigger_less:
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

    # if not util.get_args_flag("triggerless"):
    if not unit.trigger_less:
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
        logger.warning(
            'terminate org unit called without "from" in "validity"',
        )
        return common._create_virkning(_get_valid_to(unit.to_date), "infinity")

    raise exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
        key="Organization Unit must be set with either 'to' or both 'from' " "and 'to'",
        unit={
            "from": unit.from_date.isoformat() if unit.from_date else None,
            "to": unit.to_date.isoformat() if unit.to_date else None,
        },
    )


def _get_valid_from(from_date: Optional[datetime.date]) -> datetime.datetime:
    if not from_date or not isinstance(from_date, datetime.date):
        raise exceptions.ErrorCodes.V_MISSING_START_DATE()

    dt = datetime.datetime.combine(from_date, datetime.datetime.min.time())
    if dt.time() != datetime.time.min:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            "{!r} is not at midnight!".format(dt.isoformat()),
        )

    return _apply_default_tz(dt)


def _get_valid_to(to_date: Optional[datetime.date]) -> datetime.datetime:
    if not to_date:
        return POSITIVE_INFINITY

    dt = datetime.datetime.combine(to_date, datetime.datetime.min.time())
    if dt.time() != datetime.time.min:
        exceptions.ErrorCodes.E_INVALID_INPUT(
            "{!r} is not at midnight!".format(dt.isoformat()),
        )

    return _apply_default_tz(dt + ONE_DAY)


def _create_trigger_dict_from_org_unit_input(
    unit: OrganizationUnitTerminateInput,
) -> dict:
    uuid_str = str(unit.uuid)

    # create trigger dict request
    validity = {}
    if unit.from_date:
        validity[mapping.FROM] = unit.from_date.isoformat()
    if unit.to_date:
        validity[mapping.TO] = unit.to_date.isoformat()

    trigger_request = {
        mapping.TYPE: mapping.ORG_UNIT,
        mapping.UUID: uuid_str,
        mapping.VALIDITY: validity,
    }

    # Create the return dict
    trigger_dict = {
        Trigger.REQUEST_TYPE: mapping.RequestType.TERMINATE,
        Trigger.REQUEST: trigger_request,
        Trigger.ROLE_TYPE: mapping.ORG_UNIT,
        Trigger.ORG_UNIT_UUID: uuid_str,
        Trigger.EVENT_TYPE: mapping.EventType.ON_BEFORE,
        Trigger.UUID: uuid_str,
        Trigger.RESULT: None,
    }

    return trigger_dict


def _apply_default_tz(dt: datetime.datetime) -> datetime.datetime:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=util.DEFAULT_TIMEZONE)
    else:
        dt = dt.astimezone(util.DEFAULT_TIMEZONE)

    return dt
