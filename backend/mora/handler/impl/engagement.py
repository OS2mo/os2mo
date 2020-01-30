# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import reading
from ... import common
from ... import mapping
from ... import util
from ...exceptions import ErrorCodes
from ...service import employee
from ...service import facet
from ...service import orgunit

ROLE_TYPE = "engagement"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class EngagementReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ENGAGEMENT_KEY

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        job_function = mapping.JOB_FUNCTION_FIELD.get_uuid(effect)
        engagement_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        primary = mapping.PRIMARY_FIELD.get_uuid(effect)
        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        fraction = extensions.get("fraktion", None)

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        r = {
            **base_obj,
            mapping.PERSON: employee.get_one_employee(c, person),
            mapping.ORG_UNIT: orgunit.get_one_orgunit(
                c, org_unit, details=orgunit.UnitDetails.MINIMAL
            ),
            mapping.JOB_FUNCTION: facet.get_one_class(c, job_function),
            mapping.ENGAGEMENT_TYPE: facet.get_one_class(c, engagement_type),
            mapping.PRIMARY:
                facet.get_one_class(c, primary) if primary else None,
            mapping.IS_PRIMARY: cls._is_primary(c, person, primary),
            mapping.FRACTION: fraction,
        }

        return r

    @classmethod
    def _is_primary(cls, c, person, primary):

        if not util.get_args_flag("calculate_primary"):
            return None

        engagements = list(
            cls.get_lora_object(c, {'tilknyttedebrugere': person}))

        # If only engagement
        if len(engagements) <= 1:
            return True

        engagement_primary_uuids = [
            mapping.PRIMARY_FIELD.get_uuid(engagement)
            for _, engagement in engagements
        ]

        sorted_classes = cls._get_sorted_primary_class_list(c)

        for class_id, _ in sorted_classes:
            if class_id in engagement_primary_uuids:
                return class_id == primary

    @classmethod
    def _get_sorted_primary_class_list(cls, c):
        facet_id = c.facet(bvn='primary_type')[0]

        classes = [
            facet.get_one_class(c, class_id, class_obj)
            for class_id, class_obj in (c.klasse.get_all(facet=facet_id))
        ]

        # We always expect the scope value to be an int, for sorting
        try:
            parsed_classes = [
                (clazz['uuid'], int(clazz['scope']))
                for clazz in classes
            ]
        except ValueError:
            raise ErrorCodes.E_INTERNAL_ERROR(
                message="Unable to parse scope value as integer")

        # Sort based on scope values, higher is better
        sorted_classes = sorted(
            parsed_classes,
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_classes
