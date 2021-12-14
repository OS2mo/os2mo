# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task

from structlog import get_logger

from .. import reading
from ... import mapping
from ...graphapi.middleware import is_graphql
from ...request_scoped.bulking import request_wide_bulk
from ...service import employee
from ...service import facet
from ...service import orgunit
from ...service.address_handler import base
from .engagement import get_engagement
from mora import util

ROLE_TYPE = "address"

logger = get_logger()


@reading.register(ROLE_TYPE)
class AddressReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ADDRESS_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        person_uuid = mapping.USER_FIELD.get_uuid(effect)
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        address_type_uuid = mapping.ADDRESS_TYPE_FIELD.get_uuid(effect)
        engagement_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)
        visibility_uuid = mapping.USER_FIELD.get_uuid(effect)

        scope = mapping.ADDRESSES_FIELD(effect)[0].get("objekttype")
        handler = await base.get_handler_for_scope(scope).from_effect(effect)

        base_obj_task = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid)
        )

        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        address_task = create_task(
            handler.get_mo_address_and_properties(only_primary_uuid)
        )

        # Return early if flat model is desired
        if is_graphql():
            base_obj = await base_obj_task

            address_obj = await address_task
            print(address_obj)

            return {
                **base_obj,
                "value": address_obj[mapping.VALUE],
                "value2": address_obj[mapping.VALUE2],
                "address_type_uuid": address_type_uuid,
                "person_uuid": person_uuid,
                "org_unit_uuid": org_unit_uuid,
                "engagement_uuid": engagement_uuid,
                "visibility_uuid": visibility_uuid,
            }

        facet_task = create_task(
            facet.request_bulked_get_one_class_full(
                address_type_uuid, only_primary_uuid=only_primary_uuid
            )
        )

        if person_uuid:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person_uuid, only_primary_uuid=only_primary_uuid
                )
            )

        if org_unit_uuid:
            org_unit_task = create_task(
                orgunit.request_bulked_get_one_orgunit(
                    org_unit_uuid,
                    details=orgunit.UnitDetails.MINIMAL,
                    only_primary_uuid=only_primary_uuid,
                )
            )

        if engagement_uuid is not None:
            engagement = {mapping.UUID: engagement_uuid}
            if not only_primary_uuid:
                engagement = await get_engagement(
                    request_wide_bulk.connector, uuid=engagement_uuid
                )

        r = {
            **await base_obj_task,
            mapping.ADDRESS_TYPE: await facet_task,
            **await address_task,
        }

        if person_uuid:
            r[mapping.PERSON] = await person_task
        if org_unit_uuid:
            r[mapping.ORG_UNIT] = await org_unit_task
        if engagement_uuid is not None:
            r[mapping.ENGAGEMENT] = engagement

        return r
