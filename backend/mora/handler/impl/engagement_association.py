# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
from asyncio import create_task
from typing import Any, Dict

import flask

from .. import reading
from ... import mapping
from ...service import facet
from ...service import orgunit

ROLE_TYPE = mapping.ENGAGEMENT_ASSOCIATION_KEY

logger = logging.getLogger(__name__)

MO_OBJ_TYPE = Dict[str, Any]


@reading.register(ROLE_TYPE)
class AssociationReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ENGAGEMENT_ASSOCIATION_KEY

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        # person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        association_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        # substitute_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)

        only_primary_uuid = flask.request.args.get('only_primary_uuid')
        # need_sub = substitute_uuid and util.is_substitute_allowed(association_type)
        # substitute = None
        # if need_sub:
        #     substitute = create_task(employee.request_bulked_get_one_employee(
        #         substitute_uuid, only_primary_uuid=only_primary_uuid))
        # classes = list(mapping.ORG_FUNK_CLASSES_FIELD.get_uuids(effect))

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))

        # dynamic_classes_awaitable = cls.__dynamic_classes_helper(
        #     classes,
        #     only_primary_uuid=only_primary_uuid)

        # if person:
        #     person_task = create_task(
        #         employee.request_bulked_get_one_employee(
        #             person, only_primary_uuid=only_primary_uuid))

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(org_unit,
                                                   details=orgunit.UnitDetails.MINIMAL,
                                                   only_primary_uuid=only_primary_uuid))

        association_type_task = create_task(facet.request_bulked_get_one_class_full(
            association_type, only_primary_uuid=only_primary_uuid))
        r = {
            **await base_obj,
            # mapping.PERSON: (await person_task) if person else None,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ENGAGEMENT_ASSOCIATION_TYPE: await association_type_task,
            # mapping.PRIMARY: await primary_task if primary else None,
            # mapping.CLASSES: await dynamic_classes_awaitable,
            # mapping.SUBSTITUTE: await substitute if need_sub else None
        }

        return r
