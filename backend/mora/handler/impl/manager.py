#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import logging
import operator

from .. import reading
from ... import common
from ... import mapping
from ... import util
from ...service import address
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "manager"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class ManagerReader(reading.OrgFunkReadingHandler):
    function_key = mapping.MANAGER_KEY

    @classmethod
    def get_from_type(cls, c, type, object_id):

        if util.get_args_flag("inherit_manager"):
            return cls.get_inherited_manager(c, type, object_id)

        return super().get_from_type(c, type, object_id)

    @classmethod
    def get_inherited_manager(cls, c, type, object_id):

        search_fields = {
            cls.SEARCH_FIELDS[type]: object_id
        }

        manager = list(super().get(c, search_fields))

        if not manager:
            ou = orgunit.get_one_orgunit(
                c, object_id, details=orgunit.UnitDetails.FULL
            )
            try:
                parent_id = ou[mapping.PARENT][mapping.UUID]
            except (TypeError, KeyError):
                return manager

            return cls.get_inherited_manager(c, type, parent_id)

        return manager

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        manager_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        manager_level = mapping.MANAGER_LEVEL_FIELD.get_uuid(effect)
        addresses = list(mapping.FUNCTION_ADDRESS_FIELD.get_uuids(effect))
        responsibilities = list(mapping.RESPONSIBILITY_FIELD.get_uuids(effect))
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        func = {
            **base_obj,
            mapping.RESPONSIBILITY: [
                facet.get_one_class(c, obj_uuid) for obj_uuid in responsibilities
            ],
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ),
            mapping.ADDRESS: [],
        }

        for address_uuid in addresses:
            orgfunc = c.organisationfunktion.get(uuid=address_uuid)
            try:
                addr = address.get_one_address(orgfunc)
            except IndexError:
                # empty ["relationer"]["adresser"]
                continue
            addr["address_type"] = address.get_address_type(orgfunc)
            addr["uuid"] = address_uuid
            func[mapping.ADDRESS].append(addr)

        func[mapping.ADDRESS] = sorted(
            func[mapping.ADDRESS], key=operator.itemgetter(mapping.NAME)
        )

        if person:
            func[mapping.PERSON] = employee.get_one_employee(c, person)
        else:
            func[mapping.PERSON] = None

        if manager_type:
            func[mapping.MANAGER_TYPE] = facet.get_one_class(c, manager_type)
        else:
            func[mapping.MANAGER_TYPE] = None

        if manager_level:
            func[mapping.MANAGER_LEVEL] = facet.get_one_class(c, manager_level)
        else:
            func[mapping.MANAGER_LEVEL] = None

        return func
