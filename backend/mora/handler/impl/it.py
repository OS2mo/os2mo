# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from structlog import get_logger
from asyncio import create_task

from .. import reading
from ... import mapping
from ...request_scoped.query_args import current_query
from ...service import employee
from ...service import itsystem
from ...service import orgunit

ROLE_TYPE = "it"

logger = get_logger()


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ITSYSTEM_KEY

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        it_system = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid)
        )

        only_primary_uuid = current_query.args.get("only_primary_uuid")
        it_system_task = create_task(
            itsystem.request_bulked_get_one_itsystem(
                it_system, only_primary_uuid=only_primary_uuid
            )
        )

        if person:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person, only_primary_uuid=only_primary_uuid
                )
            )

        if org_unit:
            org_unit_task = await create_task(
                orgunit.request_bulked_get_one_orgunit(
                    org_unit,
                    details=orgunit.UnitDetails.MINIMAL,
                    only_primary_uuid=only_primary_uuid,
                )
            )

        r = {**await base_obj, mapping.ITSYSTEM: await it_system_task}

        if person:
            r[mapping.PERSON] = await person_task
        else:
            r[mapping.PERSON] = None

        if org_unit:
            r[mapping.ORG_UNIT] = await org_unit_task
        else:
            r[mapping.ORG_UNIT] = None

        return r
