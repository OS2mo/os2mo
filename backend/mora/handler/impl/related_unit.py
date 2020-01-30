# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import reading
from ... import common
from ... import mapping
from ...service import orgunit

ROLE_TYPE = "related_unit"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.RELATED_UNIT_KEY

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        org_units = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        parsed_org_units = [
            orgunit.get_one_orgunit(c, org_unit_uuid,
                                    details=orgunit.UnitDetails.MINIMAL)
            for org_unit_uuid in org_units
        ]
        sorted_org_units = sorted(parsed_org_units, key=lambda x: x.get('name'))

        r = {
            **base_obj,
            mapping.ORG_UNIT: sorted_org_units,
        }

        return r
