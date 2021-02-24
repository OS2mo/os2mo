# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import create_task

import flask

from .. import reading
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
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        role_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))
        only_primary_uuid = flask.request.args.get('only_primary_uuid')

        person_task = create_task(
            employee.request_bulked_get_one_employee(
                person,
                only_primary_uuid=only_primary_uuid))

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(org_unit,
                                                   details=orgunit.UnitDetails.MINIMAL,
                                                   only_primary_uuid=only_primary_uuid))
        role_type_task = create_task(
            facet.request_bulked_get_one_class_full(role_type,
                                                    only_primary_uuid=only_primary_uuid)
        )

        r = {
            **await base_obj,
            mapping.PERSON: await person_task,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ROLE_TYPE: await role_type_task,
        }

        return r
