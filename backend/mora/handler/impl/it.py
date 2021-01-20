# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import create_task

from .. import reading
from ... import common
from ... import mapping
from ...service import employee
from ...service import itsystem
from ...service import orgunit

ROLE_TYPE = "it"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ITSYSTEM_KEY

    @classmethod
    async def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        it_system = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)

        base_obj = create_task(
            super().get_mo_object_from_effect(effect, start, end, funcid))
        it_system_task = create_task(itsystem.get_one_itsystem(c, it_system))

        if person:
            person_task = create_task(employee.get_one_employee(c, person))

        if org_unit:
            org_unit_task = create_task(orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ))

        r = {**await base_obj,
             mapping.ITSYSTEM: await it_system_task}

        if person:
            r[mapping.PERSON] = await person_task
        else:
            r[mapping.PERSON] = None

        if org_unit:
            r[mapping.ORG_UNIT] = await org_unit_task
        else:
            r[mapping.ORG_UNIT] = None

        return r
