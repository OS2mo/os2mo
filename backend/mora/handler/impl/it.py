# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task

from structlog import get_logger

from .. import reading
from ... import mapping
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import itsystem
from ...service import orgunit
from mora import util

ROLE_TYPE = "it"

logger = get_logger()


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ITSYSTEM_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        person_uuid = mapping.USER_FIELD.get_uuid(effect)
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        itsystem_uuid = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)

        base_obj = await create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid)
        )

        if is_graphql():
            return {
                **base_obj,
                "person_uuid": person_uuid,
                "org_unit_uuid": org_unit_uuid,
                "itsystem_uuid": itsystem_uuid,
            }

        only_primary_uuid = util.get_args_flag("only_primary_uuid")
        it_system_task = create_task(
            itsystem.request_bulked_get_one_itsystem(
                itsystem_uuid, only_primary_uuid=only_primary_uuid
            )
        )

        if person_uuid:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person_uuid, only_primary_uuid=only_primary_uuid
                )
            )

        if org_unit_uuid:
            org_unit_task = await create_task(
                orgunit.request_bulked_get_one_orgunit(
                    org_unit_uuid,
                    details=orgunit.UnitDetails.MINIMAL,
                    only_primary_uuid=only_primary_uuid,
                )
            )

        r = {
            **base_obj,
            mapping.ITSYSTEM: await it_system_task,
            mapping.PERSON: await person_task if person_uuid else None,
            mapping.ORG_UNIT: await org_unit_task if org_unit_uuid else None,
        }

        return r
