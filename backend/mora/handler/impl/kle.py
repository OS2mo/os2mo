# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import create_task, gather

from .. import reading
from ... import common
from ... import mapping
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "kle"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class KLEReader(reading.OrgFunkReadingHandler):
    function_key = mapping.KLE_KEY

    @classmethod
    async def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        address_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = create_task(
            super().get_mo_object_from_effect(effect, start, end, funcid))

        kle_types = list(mapping.KLE_ASPECT_FIELD.get_uuids(effect))

        kle_aspect = gather(
            *[create_task(facet.get_one_class_full(c, obj_uuid)) for obj_uuid in
              kle_types])
        kle_number_task = create_task(facet.get_one_class_full(c, address_type))
        org_unit_task = create_task(
            orgunit.get_one_orgunit(c, org_unit, details=orgunit.UnitDetails.MINIMAL))

        r = {
            **await base_obj,
            mapping.KLE_ASPECT: await kle_aspect,
            mapping.KLE_NUMBER: await kle_number_task,
            mapping.ORG_UNIT: await org_unit_task,
        }

        return r
