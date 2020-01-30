# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import reading
from ... import common
from ... import mapping
from ...service import employee
from ...service import itsystem
from ...service import orgunit

ROLE_TYPE = "it"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ITSYSTEM_KEY

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        it_system = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        r = {**base_obj, mapping.ITSYSTEM: itsystem.get_one_itsystem(c, it_system)}

        if person:
            r[mapping.PERSON] = employee.get_one_employee(c, person)
        else:
            r[mapping.PERSON] = None

        if org_unit:
            r[mapping.ORG_UNIT] = orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            )
        else:
            r[mapping.ORG_UNIT] = None

        return r
