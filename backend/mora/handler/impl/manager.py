# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task
from asyncio import gather
from datetime import datetime
from typing import Any
from typing import Awaitable
from typing import Dict
from typing import Iterable
from typing import Optional

from structlog import get_logger

from .. import reading
from ... import mapping
from ... import util
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "manager"

logger = get_logger()


@reading.register(ROLE_TYPE)
class ManagerReader(reading.OrgFunkReadingHandler):
    function_key = mapping.MANAGER_KEY

    @classmethod
    async def get_from_type(
        cls, c, type, object_id, changed_since: Optional[datetime] = None
    ):

        if util.get_args_flag("inherit_manager"):
            return await cls.get_inherited_manager(c, type, object_id)

        return await super().get_from_type(c, type, object_id)

    @classmethod
    async def get_inherited_manager(cls, c, type, object_id):

        search_fields = {cls.SEARCH_FIELDS[type]: object_id}

        manager = list(await super().get(c, search_fields))

        if not manager:
            only_primary_uuid = util.get_args_flag("only_primary_uuid")
            ou = await orgunit.get_one_orgunit(
                c,
                object_id,
                details=orgunit.UnitDetails.FULL,
                only_primary_uuid=only_primary_uuid,
            )
            try:
                parent_id = ou[mapping.PARENT][mapping.UUID]
            except (TypeError, KeyError):
                return manager

            return await cls.get_inherited_manager(c, type, parent_id)

        return manager

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):

        person = mapping.USER_FIELD.get_uuid(effect)
        manager_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        manager_level = mapping.MANAGER_LEVEL_FIELD.get_uuid(effect)
        responsibilities = list(mapping.RESPONSIBILITY_FIELD.get_uuids(effect))
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)

        base_obj = await create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid)
        )

        if is_graphql():
            return {
                **base_obj,
                "person_uuid": person,
                "manager_type_uuid": manager_type,
                "manager_level_uuid": manager_level,
                "responsibility_uuids": responsibilities,
                "org_unit_uuid": org_unit,
            }

        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        if person:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person, only_primary_uuid=only_primary_uuid
                )
            )

        if manager_type:
            manager_type_task = create_task(
                facet.request_bulked_get_one_class_full(
                    manager_type, only_primary_uuid=only_primary_uuid
                )
            )

        if manager_level:
            manager_level_task = create_task(
                facet.request_bulked_get_one_class_full(
                    manager_level, only_primary_uuid=only_primary_uuid
                )
            )

        resp_tasks: Iterable[Awaitable] = await gather(
            *[
                create_task(
                    facet.request_bulked_get_one_class_full(
                        obj_uuid, only_primary_uuid=only_primary_uuid
                    )
                )
                for obj_uuid in responsibilities
            ]
        )

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(
                org_unit,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
        )

        func: Dict[Any, Any] = {
            **base_obj,
            mapping.RESPONSIBILITY: gather(*resp_tasks),
            mapping.ORG_UNIT: await org_unit_task,
        }

        if person:
            func[mapping.PERSON] = await person_task
        else:
            func[mapping.PERSON] = None

        if manager_type:
            func[mapping.MANAGER_TYPE] = await manager_type_task
        else:
            func[mapping.MANAGER_TYPE] = None

        if manager_level:
            func[mapping.MANAGER_LEVEL] = await manager_level_task
        else:
            func[mapping.MANAGER_LEVEL] = None

        return func
