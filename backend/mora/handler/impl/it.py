# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from mora import util
from mora.common import get_connector
from mora.request_scoped.bulking import get_lora_object

from ... import mapping
from ...graphapi.middleware import is_graphql
from ...lora import LoraObjectType
from ...service import employee
from ...service import facet
from ...service import orgunit
from .. import reading
from .engagement import get_engagement

ROLE_TYPE = "it"

logger = get_logger()


async def noop_task() -> None:  # pragma: no cover
    """Noop task.

    Returns:
        None.
    """
    return None


async def get_itsystem_only_primary(itsystem_uuid):
    """Task to return a limited itsystem response."""
    return {mapping.UUID: itsystem_uuid}


async def get_itsystem(itsystem_uuid):
    """Task to return a full itsystem response."""
    system = await get_lora_object(type_=LoraObjectType.it_system, uuid=itsystem_uuid)
    system_attrs = system["attributter"]["itsystemegenskaber"][0]
    return {
        "uuid": itsystem_uuid,
        "name": system_attrs.get("itsystemnavn"),
        "reference": system_attrs.get("konfigurationreference"),
        "system_type": system_attrs.get("itsystemtype"),
        "user_key": system_attrs.get("brugervendtnoegle"),
        mapping.VALIDITY: util.get_effect_validity(
            system["tilstande"]["itsystemgyldighed"][0],
        ),
    }


@reading.register(ROLE_TYPE)
class ItSystemBindingReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ITSYSTEM_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        person_uuid = mapping.USER_FIELD.get_uuid(effect)
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        itsystem_uuid = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)
        primary_uuid = mapping.PRIMARY_FIELD.get_uuid(effect)
        # Emptied lists of engagements contains an empty uuid which we need to remove:
        engagement_uuids = list(mapping.ASSOCIATED_FUNCTION_FIELD.get_uuids(effect))

        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        external_id = extensions.get(mapping.EXTENSION_1)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        if is_graphql():
            return {
                **base_obj,
                "employee_uuid": person_uuid,
                "org_unit_uuid": org_unit_uuid,
                "engagement_uuids": engagement_uuids,
                "itsystem_uuid": itsystem_uuid,
                "primary_uuid": primary_uuid,
                "external_id": external_id,
            }

        r = {
            **base_obj,
            mapping.PERSON: None,
            mapping.ORG_UNIT: None,
            mapping.PRIMARY: None,
            mapping.ENGAGEMENT: None,
        }

        if only_primary_uuid:
            r[mapping.ITSYSTEM] = await get_itsystem_only_primary(itsystem_uuid)
        else:
            r[mapping.ITSYSTEM] = await get_itsystem(itsystem_uuid)

        if person_uuid:
            r[mapping.PERSON] = await employee.request_bulked_get_one_employee(
                person_uuid, only_primary_uuid=only_primary_uuid
            )

        if org_unit_uuid:
            r[mapping.ORG_UNIT] = await orgunit.request_bulked_get_one_orgunit(
                org_unit_uuid,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
        if engagement_uuids:
            # For backwards compatibility we only return one engagement.
            # Use graphql to fetch more than one engagement for an ituser.
            r[mapping.ENGAGEMENT] = await get_engagement(
                get_connector(), uuid=min(engagement_uuids)
            )

        if primary_uuid:  # pragma: no cover
            r[mapping.PRIMARY] = await facet.request_bulked_get_one_class_full(
                primary_uuid, only_primary_uuid=only_primary_uuid
            )

        return r
