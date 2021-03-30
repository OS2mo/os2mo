# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import create_task

from .. import reading
from ... import mapping
from ...request_scoped.query_args import current_query
from ...service import employee
from ...service import facet
from ...service import orgunit
from ...service.address_handler import base

ROLE_TYPE = "address"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class AddressReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ADDRESS_KEY

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        address_type = mapping.ADDRESS_TYPE_FIELD.get_uuid(effect)

        scope = mapping.ADDRESSES_FIELD(effect)[0].get("objekttype")
        handler = base.get_handler_for_scope(scope).from_effect(effect)

        base_obj_task = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))
        only_primary_uuid = current_query.args.get('only_primary_uuid')

        facet_task = create_task(facet.request_bulked_get_one_class_full(
            address_type,
            only_primary_uuid=only_primary_uuid))

        address_task = create_task(
            handler.get_mo_address_and_properties(only_primary_uuid)
        )
        if person:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person,
                    only_primary_uuid=only_primary_uuid))

        if org_unit:
            org_unit_task = create_task(orgunit.request_bulked_get_one_orgunit(
                org_unit, details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid
            ))

        r = {
            **await base_obj_task,
            mapping.ADDRESS_TYPE: await facet_task,
            **await address_task,
        }
        if person:
            r[mapping.PERSON] = await person_task
        if org_unit:
            r[mapping.ORG_UNIT] = await org_unit_task

        return r
