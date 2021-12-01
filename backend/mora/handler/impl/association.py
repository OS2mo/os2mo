# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from asyncio import create_task
from asyncio import gather
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from structlog import get_logger

from .. import reading
from ... import mapping
from ... import util
from ...service import employee
from ...service import facet
from ...service import orgunit
from mora import exceptions

ROLE_TYPE = "association"
SUBSTITUTE_ASSOCIATION = {"name": "i18n:substitute_association"}
FIRST_PARTY_PERSPECTIVE = "first_party_perspective"

logger = get_logger()

MO_OBJ_TYPE = Dict[str, Any]


@reading.register(ROLE_TYPE)
class AssociationReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ASSOCIATION_KEY

    @classmethod
    async def get_from_type(
        cls, c, type, objid, changed_since: Optional[datetime] = None
    ):

        search_fields = {cls.SEARCH_FIELDS[type]: objid}
        if util.get_args_flag(FIRST_PARTY_PERSPECTIVE):
            if type != "e":  # raises
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    f"Invalid args: {FIRST_PARTY_PERSPECTIVE}"
                )
            else:
                # get both "vanilla" associations and
                # associations where "objid" is the substitute, in some new fields
                e_task = create_task(
                    cls.get(c, search_fields, changed_since=changed_since)
                )
                f_task = create_task(
                    cls.get(
                        c, {"tilknyttedefunktioner": objid}, changed_since=changed_since
                    )
                )
                e_result = await e_task
                f_result = await f_task
                augmented_e = [
                    {
                        **x,
                        "first_party_association_type": x["association_type"],
                        "third_party_associated": x["substitute"],
                        "third_party_association_type": SUBSTITUTE_ASSOCIATION
                        if x["substitute"]
                        else None,
                    }
                    for x in e_result
                ]

                augmented_f = [
                    {
                        **x,
                        "first_party_association_type": SUBSTITUTE_ASSOCIATION
                        if x["substitute"]
                        else None,
                        "third_party_associated": x["person"],
                        "third_party_association_type": x["association_type"],
                    }
                    for x in f_result
                ]

                return augmented_e + augmented_f
        else:  # default
            return await cls.get(c, search_fields, changed_since=changed_since)

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
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        association_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        substitute_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)
        only_primary_uuid = util.get_args_flag("only_primary_uuid")
        need_sub = substitute_uuid and util.is_substitute_allowed(association_type)
        substitute = None
        if need_sub:
            substitute = create_task(
                employee.request_bulked_get_one_employee(
                    substitute_uuid, only_primary_uuid=only_primary_uuid
                )
            )
        classes = list(mapping.ORG_FUNK_CLASSES_FIELD.get_uuids(effect))
        primary = mapping.PRIMARY_FIELD.get_uuid(effect)

        # Await base object
        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        # Return early if flat model is desired
        # Idea: return MORead data model here?
        if flat:
            return {
                **base_obj,
                "person_uuid": person,
                "org_unit_uuid": org_unit,
                "association_type_uuid": association_type,
                "substitute_uuid": substitute_uuid if need_sub else None,
                "dynamic_classes": classes,
                "primary_uuid": primary,
            }

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
        r = {
            **base_obj,
            mapping.PERSON: (await person_task) if person else None,
            mapping.ORG_UNIT: await org_unit_task,
            mapping.ASSOCIATION_TYPE: await association_type_task,
            mapping.PRIMARY: await primary_task if primary else None,
            mapping.CLASSES: await dynamic_classes_awaitable,
            mapping.SUBSTITUTE: await substitute if need_sub else None,
        }

        return r
