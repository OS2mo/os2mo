# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

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
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        address_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        kle_types = list(mapping.KLE_ASPECT_FIELD.get_uuids(effect))

        r = {
            **base_obj,
            mapping.KLE_ASPECT: [
                facet.get_one_class(c, obj_uuid) for obj_uuid in kle_types
            ],
            mapping.KLE_NUMBER: facet.get_one_class(c, address_type),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            )
        }

        return r
