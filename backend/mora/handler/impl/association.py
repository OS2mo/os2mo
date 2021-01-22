# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
from asyncio import create_task

from mora import exceptions

from .. import reading
from ... import common, util
from ... import mapping
from ...service import employee
from ...service import facet
from ...service import orgunit
from ...service.facet import ClassDetails

ROLE_TYPE = "association"
SUBSTITUTE_ASSOCIATION = {'name': 'i18n:substitute_association'}
FIRST_PARTY_PERSPECTIVE = 'first_party_perspective'

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class AssociationReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ASSOCIATION_KEY

    @classmethod
    async def get_from_type(cls, c, type, objid):

        search_fields = {
            cls.SEARCH_FIELDS[type]: objid
        }
        if util.get_args_flag(FIRST_PARTY_PERSPECTIVE):
            if type != 'e':  # raises
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    f'Invalid args: {FIRST_PARTY_PERSPECTIVE}')
            else:
                # get both "vanilla" associations and
                # associations where "objid" is the substitute, in some new fields
                e_task = create_task(cls.get(c, search_fields))
                f_task = create_task(cls.get(c, {'tilknyttedefunktioner': objid}))
                e_result = await e_task
                f_result = await f_task
                augmented_e = [{**x,
                                'first_party_association_type': x['association_type'],
                                'third_party_associated': x['substitute'],
                                'third_party_association_type':
                                    SUBSTITUTE_ASSOCIATION if x[
                                        'substitute'] else None,
                                } for x in e_result]

                augmented_f = [{**x,
                                'first_party_association_type':
                                    SUBSTITUTE_ASSOCIATION if x[
                                        'substitute'] else None,
                                'third_party_associated': x['person'],
                                'third_party_association_type': x['association_type'],
                                } for x in f_result]

                return augmented_e + augmented_f
        else:  # default
            return await cls.get(c, search_fields)

    @classmethod
    async def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        association_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        substitute_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)
        substitute = None
        if substitute_uuid and util.is_substitute_allowed(association_type):
            substitute = await employee.get_one_employee(c, substitute_uuid)
        classes = list(mapping.ORG_FUNK_CLASSES_FIELD.get_uuids(effect))
        primary = mapping.PRIMARY_FIELD.get_uuid(effect)

        base_obj = create_task(
            super().get_mo_object_from_effect(effect, start, end, funcid))

        # Fetch all classes in bulk
        all_classes = classes + [association_type] + ([primary] if primary else [])

        class_details = {
            ClassDetails.FULL_NAME,
            ClassDetails.TOP_LEVEL_FACET,
            ClassDetails.FACET
        }
        fetched_classes_task = create_task(
            facet.get_bulk_classes(c, all_classes, details=class_details))

        person_task = create_task(employee.get_one_employee(c, person))
        org_unit_task = create_task(
            orgunit.get_one_orgunit(c, org_unit, details=orgunit.UnitDetails.MINIMAL))

        # Pull out each class
        fetched_classes = await fetched_classes_task
        association_type_class = fetched_classes.pop(association_type)
        primary_class = fetched_classes.pop(primary, None)
        dynamic_classes = fetched_classes

        r = {
            **await base_obj,
            mapping.PERSON: await person_task,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ASSOCIATION_TYPE: association_type_class,
            mapping.PRIMARY: primary_class,
            mapping.CLASSES: list(dynamic_classes.values()),
            mapping.SUBSTITUTE: substitute
        }

        return r
