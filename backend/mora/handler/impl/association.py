# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import reading
from ... import common
from ... import mapping
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "association"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class AssociationReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ASSOCIATION_KEY

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        association_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        primary = mapping.PRIMARY_FIELD.get_uuid(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        r = {
            **base_obj,
            mapping.PERSON: employee.get_one_employee(c, person),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ),
            mapping.ASSOCIATION_TYPE: facet.get_one_class(c, association_type),
            mapping.PRIMARY: facet.get_one_class(
                c, primary) if primary else None,
        }

        return r
