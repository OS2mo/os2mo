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
        classes = list(mapping.ORG_FUNK_CLASSES_FIELD.get_uuids(effect))
        primary = mapping.PRIMARY_FIELD.get_uuid(effect)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        # Fetch all classes in bulk
        all_classes = classes + [association_type] + ([primary] if primary else [])
        fetched_classes = facet.get_bulk_classes(c, all_classes)
        # Pull out each class
        association_type_class = fetched_classes.pop(association_type)
        primary_class = fetched_classes.pop(primary, None)
        dynamic_classes = fetched_classes

        r = {
            **base_obj,
            mapping.PERSON: employee.get_one_employee(c, person),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ),
            mapping.ASSOCIATION_TYPE: association_type_class,
            mapping.PRIMARY: primary_class,
            mapping.CLASSES: list(dynamic_classes.values())
        }

        return r
