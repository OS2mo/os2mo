# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from mora import util
from structlog import get_logger
from asyncio import create_task, gather

from .. import reading
from ... import mapping
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "kle"

logger = get_logger()


@reading.register(ROLE_TYPE)
class KLEReader(reading.OrgFunkReadingHandler):
    function_key = mapping.KLE_KEY

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        address_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))

        kle_types = list(mapping.KLE_ASPECT_FIELD.get_uuids(effect))
        only_primary_uuid = util.get_args_flag('only_primary_uuid')

        # via tasks, await request_bulked_get_one_class_full, then prepare a gather of
        # those (resulting) promises for later collection
        kle_aspect = gather(*await gather(
            *[create_task(facet.request_bulked_get_one_class_full(
                obj_uuid, only_primary_uuid=only_primary_uuid)) for obj_uuid in
                kle_types]))
        kle_number_task = create_task(facet.request_bulked_get_one_class_full(
            address_type, only_primary_uuid=only_primary_uuid))

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(org_unit,
                                                   details=orgunit.UnitDetails.MINIMAL,
                                                   only_primary_uuid=only_primary_uuid))

        r = {
            **await base_obj,
            mapping.KLE_ASPECT: await kle_aspect,
            mapping.KLE_NUMBER: await kle_number_task,
            mapping.ORG_UNIT: await org_unit_task,
        }

        return r
