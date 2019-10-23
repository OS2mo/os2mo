#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
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

        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        primary = extensions.get("primær", None)
        print(primary)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        r = {
            **base_obj,
            mapping.PERSON: employee.get_one_employee(c, person),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ),
            mapping.ASSOCIATION_TYPE: facet.get_one_class(c, association_type),
            mapping.PRIMARY: primary,
        }

        return r
