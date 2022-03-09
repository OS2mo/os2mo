# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task
from asyncio import gather
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from more_itertools import partition
from structlog import get_logger

from .it import ItSystemBindingReader
from .. import reading
from ... import mapping
from ... import util
from ...common import get_connector
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import facet
from ...service import orgunit
from mora import exceptions

ROLE_TYPE = "association"
SUBSTITUTE_ASSOCIATION = {"name": "i18n:substitute_association"}
MO_OBJ_TYPE = Dict[str, Any]

logger = get_logger()


class AssociationSubType(Enum):
    NORMAL = None

    # only valid for employee associations
    FIRST_PARTY_PERSPECTIVE = "first_party_perspective"

    # "IT association"
    IT = mapping.IT


class ResponseExtraField(Enum):
    NONE = None
    SUBSTITUTE = "substitute"
    JOB_FUNCTION = "job_function"


@reading.register(ROLE_TYPE)
class AssociationReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ASSOCIATION_KEY

    @classmethod
    async def get_from_type(
        cls, c, type, objid, changed_since: Optional[datetime] = None
    ):
        search_fields = {cls.SEARCH_FIELDS[type]: objid}

        # Get *all* associations for this employee or org unit
        assocs = await cls.get(c, search_fields, changed_since=changed_since)

        if util.get_args_flag(AssociationSubType.FIRST_PARTY_PERSPECTIVE.value):
            # URL contains "?first_party_perspective=1"
            if type == "e":
                return await cls._get_first_party_perspective(
                    c, objid, assocs, changed_since=changed_since
                )
            else:
                # "?first_party_perspective=1" is only valid for employees (not org
                # units.)
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    f"Invalid args: {AssociationSubType.FIRST_PARTY_PERSPECTIVE.value}"
                )
        elif util.get_args_flag(AssociationSubType.IT.value):
            # URL contains "?it=1"
            return cls._get_it_associations(assocs)
        else:
            # URL contains neither "?first_party_perspective=1" nor "?it=1"
            return cls._get_normal_associations(assocs)

    @classmethod
    def _partition_assocs(cls, assocs: Iterable[dict]):
        # Divide associations into IT associations and normal associations
        normal_assocs, it_assocs = partition(
            lambda assoc: assoc.get(mapping.IT), assocs
        )
        return normal_assocs, it_assocs

    @classmethod
    def _get_it_associations(cls, assocs: Iterable[dict]):
        normal_assocs, it_assocs = cls._partition_assocs(assocs)
        return it_assocs

    @classmethod
    def _get_normal_associations(cls, assocs: Iterable[dict]):
        normal_assocs, it_assocs = cls._partition_assocs(assocs)
        return normal_assocs

    @classmethod
    async def _get_first_party_perspective(
        cls,
        c,
        objid,
        assocs: Iterable[dict],
        changed_since: Optional[datetime] = None,
    ):
        normal_assocs = cls._get_normal_associations(assocs)
        # Fetch associations linked to this employee by the relation
        # 'tilknyttedefunktioner'
        substitute_assocs = await cls.get(
            c, {"tilknyttedefunktioner": objid}, changed_since=changed_since
        )
        substitute_assocs = list(substitute_assocs)
        # Remove any "IT associations"
        substitute_assocs = filter(
            lambda assoc: assoc.get(mapping.IT) is None, substitute_assocs
        )
        # Return a decorated result composed of both `normal_assocs` and
        # `substitute_assocs`.
        return cls._get_substitute_pairs(normal_assocs, substitute_assocs)

    @classmethod
    def _get_substitute_pairs(
        cls, normal_assocs: Iterable[dict], substitute_assocs: Iterable[dict]
    ):
        # get both "vanilla" associations and
        # associations where "objid" is the substitute, in some new fields
        augmented_normal = [
            {
                **x,
                "first_party_association_type": x["association_type"],
                "third_party_associated": x["substitute"],
                "third_party_association_type": SUBSTITUTE_ASSOCIATION
                if x["substitute"]
                else None,
            }
            for x in normal_assocs
        ]
        augmented_substitutes = [
            {
                **x,
                "first_party_association_type": SUBSTITUTE_ASSOCIATION
                if x["substitute"]
                else None,
                "third_party_associated": x["person"],
                "third_party_association_type": x["association_type"],
            }
            for x in substitute_assocs
        ]
        return augmented_normal + augmented_substitutes

    @staticmethod
    async def __dynamic_classes_helper(
        classes: Iterable[str], only_primary_uuid: bool = False
    ) -> List[MO_OBJ_TYPE]:
        """
        helper, is an awaitable, that will gather a bunch of classes in a list
        :param classes:
        :return: list of classes (AT LEAST) bulked together
        """

        return await gather(
            *[
                await facet.request_bulked_get_one_class_full(
                    cla, only_primary_uuid=only_primary_uuid
                )
                for cla in classes
            ]
        )

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        association_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        classes = list(mapping.ORG_FUNK_CLASSES_FIELD.get_uuids(effect))
        primary = mapping.PRIMARY_FIELD.get_uuid(effect)

        associated_function_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)
        it_system_binding_uuid = mapping.SINGLE_ITSYSTEM_FIELD.get_uuid(effect)

        # If an IT system binding is present, `associated_function_uuid`
        # identifies a job function.
        # Otherwise, it identifies a substitute, and must be validated as such.
        if it_system_binding_uuid:
            extra = ResponseExtraField.JOB_FUNCTION
        elif associated_function_uuid and util.is_substitute_allowed(association_type):
            extra = ResponseExtraField.SUBSTITUTE
        else:
            extra = ResponseExtraField.NONE

        # Await base object
        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        if is_graphql():
            return {
                **base_obj,
                "employee_uuid": person,
                "org_unit_uuid": org_unit,
                "association_type_uuid": association_type,
                "dynamic_classes": classes,
                "primary_uuid": primary,
                "substitute_uuid": (
                    associated_function_uuid
                    if (extra == ResponseExtraField.SUBSTITUTE)
                    else None
                ),
                "job_function_uuid": (
                    associated_function_uuid
                    if (extra == ResponseExtraField.JOB_FUNCTION)
                    else None
                ),
                "it_user_uuid": it_system_binding_uuid,
            }

        substitute = None
        if extra == ResponseExtraField.SUBSTITUTE:
            substitute = create_task(
                employee.request_bulked_get_one_employee(
                    associated_function_uuid, only_primary_uuid=only_primary_uuid
                )
            )

        # Create awaitables for bulky objects
        dynamic_classes_awaitable = cls.__dynamic_classes_helper(
            classes, only_primary_uuid=only_primary_uuid
        )

        if person:
            person_task = create_task(
                employee.request_bulked_get_one_employee(
                    person, only_primary_uuid=only_primary_uuid
                )
            )

        org_unit_task = create_task(
            orgunit.request_bulked_get_one_orgunit(
                org_unit,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
        )

        if association_type:
            association_type_task = create_task(
                facet.request_bulked_get_one_class_full(
                    association_type, only_primary_uuid=only_primary_uuid
                )
            )

        if primary:
            primary_task = create_task(
                facet.request_bulked_get_one_class_full(
                    primary, only_primary_uuid=only_primary_uuid
                )
            )

        if it_system_binding_uuid:
            # This probably breaks some architectural pattern in MO, but I
            # don't know a better way at this point.
            c = get_connector()
            reader = ItSystemBindingReader()
            it_system_binding_task = reader.get(
                c,
                {mapping.UUID: it_system_binding_uuid},
            )

        if extra == ResponseExtraField.JOB_FUNCTION and associated_function_uuid:
            c = get_connector()
            job_function_task = facet.get_one_class(
                c,
                classid=associated_function_uuid,
                details=set(),
                only_primary_uuid=only_primary_uuid,
            )
        else:
            job_function_task = None

        r = {
            **base_obj,
            mapping.PERSON: (await person_task) if person else None,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ASSOCIATION_TYPE: (
                (await association_type_task) if association_type else None
            ),
            mapping.PRIMARY: (await primary_task) if primary else None,
            mapping.CLASSES: await dynamic_classes_awaitable,
            mapping.SUBSTITUTE: (
                (await substitute) if extra == ResponseExtraField.SUBSTITUTE else None
            ),
            mapping.JOB_FUNCTION: (
                (await job_function_task) if job_function_task else None
            ),
            mapping.IT: (
                (await it_system_binding_task) if it_system_binding_uuid else None
            ),
        }

        return r
