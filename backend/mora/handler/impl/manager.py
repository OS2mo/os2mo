# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
import operator
from asyncio import create_task, gather
from typing import Any, Awaitable, Dict, Iterable, Optional

import flask

from .. import reading
from ... import mapping
from ... import util
from ...request_wide_bulking import request_wide_bulk
from ...service import address
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "manager"

logger = logging.getLogger(__name__)


async def address_helper(c, address_uuid) -> Optional[Dict[Any, Any]]:
    orgfunc = await c.organisationfunktion.get(uuid=address_uuid)
    try:
        addr = await address.get_one_address(orgfunc)
    except IndexError:
        # empty ["relationer"]["adresser"]
        return None
    addr["address_type"] = await address.get_address_type(orgfunc)
    addr["uuid"] = address_uuid
    return addr


@reading.register(ROLE_TYPE)
class ManagerReader(reading.OrgFunkReadingHandler):
    function_key = mapping.MANAGER_KEY

    @classmethod
    async def get_from_type(cls, c, type, object_id):

        if util.get_args_flag("inherit_manager"):
            return await cls.get_inherited_manager(c, type, object_id)

        return await super().get_from_type(c, type, object_id)

    @classmethod
    async def get_inherited_manager(cls, c, type, object_id):

        search_fields = {
            cls.SEARCH_FIELDS[type]: object_id
        }

        manager = list(await super().get(c, search_fields))

        if not manager:
            only_primary_uuid = flask.request.args.get('only_primary_uuid')
            ou = await orgunit.get_one_orgunit(
                c, object_id, details=orgunit.UnitDetails.FULL,
                only_primary_uuid=only_primary_uuid
            )
            try:
                parent_id = ou[mapping.PARENT][mapping.UUID]
            except (TypeError, KeyError):
                return manager

            return await cls.get_inherited_manager(c, type, parent_id)

        return manager

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):

        person = mapping.USER_FIELD.get_uuid(effect)
        manager_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        manager_level = mapping.MANAGER_LEVEL_FIELD.get_uuid(effect)
        addresses = list(mapping.FUNCTION_ADDRESS_FIELD.get_uuids(effect))
        responsibilities = list(mapping.RESPONSIBILITY_FIELD.get_uuids(effect))
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))
        only_primary_uuid = flask.request.args.get('only_primary_uuid')

        if person:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person,
                    only_primary_uuid=only_primary_uuid))

        if manager_type:
            manager_type_task = create_task(
                facet.request_bulked_get_one_class_full(
                    manager_type,
                    only_primary_uuid=only_primary_uuid))

        if manager_level:
            manager_level_task = create_task(
                facet.request_bulked_get_one_class_full(
                    manager_level,
                    only_primary_uuid=only_primary_uuid))

        resp_tasks: Iterable[Awaitable] = await gather(
            *[create_task(facet.request_bulked_get_one_class_full(
                obj_uuid, only_primary_uuid=only_primary_uuid))
                for obj_uuid in responsibilities])

        org_unit_task = create_task(orgunit.request_bulked_get_one_orgunit(
            org_unit, details=orgunit.UnitDetails.MINIMAL,
            only_primary_uuid=only_primary_uuid
        ))

        address_tasks = [
            create_task(address_helper(request_wide_bulk.connector, address_uuid))
            for address_uuid in addresses]

        func: Dict[Any, Any] = {
            **await base_obj,
            mapping.RESPONSIBILITY: gather(*resp_tasks),
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ADDRESS: [],
        }

        addr_results = await gather(*address_tasks)
        func[mapping.ADDRESS].extend([addr for addr in addr_results
                                      if addr is not None])

        func[mapping.ADDRESS] = sorted(
            func[mapping.ADDRESS], key=operator.itemgetter(mapping.NAME)
        )

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
