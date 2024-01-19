# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather

from more_itertools import bucket
from more_itertools import only
from structlog import get_logger

from .. import reading
from ... import mapping
from ...graphapi.middleware import is_graphql
from ...lora import LoraObjectType
from ...service import employee
from ...service import facet
from ...service import orgunit
from .engagement import get_engagement
from mora import util
from mora.common import get_connector
from mora.request_scoped.bulking import get_lora_object

ROLE_TYPE = "it"

logger = get_logger()


async def noop_task() -> None:
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
        org_funcs = mapping.ASSOCIATED_FUNCTION_FIELD(effect)
        # Engagements and it_users are both associated functions that can be grouped by objecttype
        grouped_org_funcs = bucket(org_funcs, key=lambda o: o.get(mapping.OBJECTTYPE))
        engagements = grouped_org_funcs[mapping.ENGAGEMENT]

        engagement_uuids = {e["uuid"] for e in engagements}
        # TODO: #59192 add addresses
        # addresses = grouped_org_funcs[mapping.ADDRESS]
        # address_uuids = {a["uuid"] for a in addresses}

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        if is_graphql():
            return {
                **base_obj,
                "employee_uuid": person_uuid,
                "org_unit_uuid": org_unit_uuid,
                "engagement_uuids": engagement_uuids,
                # "address_uuids": address_uuids,
                "itsystem_uuid": itsystem_uuid,
                "primary_uuid": primary_uuid,
            }

        if only_primary_uuid:
            it_system_task = get_itsystem_only_primary(itsystem_uuid)
        else:
            it_system_task = get_itsystem(itsystem_uuid)

        if person_uuid:
            person_task = employee.request_bulked_get_one_employee(
                person_uuid, only_primary_uuid=only_primary_uuid
            )
        else:
            person_task = noop_task()

        if org_unit_uuid:
            org_unit_task = orgunit.request_bulked_get_one_orgunit(
                org_unit_uuid,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
        else:
            org_unit_task = noop_task()

        if engagement_uuids:
            engagement_task = get_engagement(
                get_connector(), uuid=only(engagement_uuids)
            )
        else:
            engagement_task = noop_task()

        if primary_uuid:
            primary_task = facet.request_bulked_get_one_class_full(
                primary_uuid, only_primary_uuid=only_primary_uuid
            )
        else:
            primary_task = noop_task()

        itsystem, person, org_unit, primary, engagement = await gather(
            it_system_task, person_task, org_unit_task, primary_task, engagement_task
        )
        return {
            **base_obj,
            mapping.ITSYSTEM: itsystem,
            mapping.PERSON: person,
            mapping.ORG_UNIT: org_unit,
            mapping.PRIMARY: primary,
            mapping.ENGAGEMENT: engagement,
        }
