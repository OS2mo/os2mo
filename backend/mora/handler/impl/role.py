# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import create_task

from .. import reading
from ... import common
from ... import mapping
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "role"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ROLE_KEY

    @classmethod
    async def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        role_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = create_task(
            super().get_mo_object_from_effect(effect, start, end, funcid))
        person_task = create_task(employee.get_one_employee(c, person))
        org_unit_task = create_task(
            orgunit.get_one_orgunit(c, org_unit, details=orgunit.UnitDetails.MINIMAL))
        role_type_task = create_task(facet.get_one_class_full(c, role_type))

        r = {
            **await base_obj,
            mapping.PERSON: await person_task,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ROLE_TYPE: await role_type_task,
        }

        return r
