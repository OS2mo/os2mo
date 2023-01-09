# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task

from structlog import get_logger

from .. import reading
from ... import mapping
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import facet
from ...service import orgunit
from mora import util

ROLE_TYPE = "role"

logger = get_logger()


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ROLE_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        person_uuid = mapping.USER_FIELD.get_uuid(effect)
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        role_type_uuid = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = await create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid)
        )
        if is_graphql():
            return {
                **base_obj,
                "employee_uuid": person_uuid,
                "org_unit_uuid": org_unit_uuid,
                "role_type_uuid": role_type_uuid,
            }

        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        person_task = create_task(
            employee.request_bulked_get_one_employee(
                person_uuid, only_primary_uuid=only_primary_uuid
            )
        )

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(
                org_unit_uuid,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
        )
        role_type_task = create_task(
            facet.request_bulked_get_one_class_full(
                role_type_uuid, only_primary_uuid=only_primary_uuid
            )
        )

        r = {
            **base_obj,
            mapping.PERSON: await person_task,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ROLE_TYPE: await role_type_task,
        }

        return r
