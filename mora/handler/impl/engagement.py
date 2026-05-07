# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from structlog import get_logger

from mora.common import get_connector

from ... import lora
from ... import mapping
from ... import util
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import facet
from ...service import orgunit
from ...service.facet import get_sorted_primary_class_list
from .. import reading

ROLE_TYPE = "engagement"

logger = get_logger()


@reading.register(ROLE_TYPE)
class EngagementReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ENGAGEMENT_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        job_function = mapping.JOB_FUNCTION_FIELD.get_uuid(effect)
        engagement_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)

        primary = mapping.PRIMARY_FIELD.get_uuid(effect)
        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        fraction = extensions.get("fraktion", None)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        if is_graphql():
            return {
                **base_obj,
                "org_unit_uuid": org_unit,
                "employee_uuid": person,
                "engagement_type_uuid": engagement_type,
                "job_function_uuid": job_function,
                "primary_uuid": primary or None,
                "fraction": fraction,
                **cls._get_extension_fields(extensions),
            }

        is_primary = await cls._is_primary(get_connector(), person, primary)
        person_obj = await employee.request_bulked_get_one_employee(
            userid=person, only_primary_uuid=only_primary_uuid
        )

        org_unit_obj = await orgunit.request_bulked_get_one_orgunit(
            unitid=org_unit,
            details=orgunit.UnitDetails.MINIMAL,
            only_primary_uuid=only_primary_uuid,
        )

        job_function_obj = await facet.request_bulked_get_one_class_full(
            job_function, only_primary_uuid=only_primary_uuid
        )
        engagement_type_obj = await facet.request_bulked_get_one_class_full(
            engagement_type, only_primary_uuid=only_primary_uuid
        )

        r = {
            **base_obj,
            mapping.PERSON: person_obj,
            mapping.ORG_UNIT: org_unit_obj,
            mapping.JOB_FUNCTION: job_function_obj,
            mapping.ENGAGEMENT_TYPE: engagement_type_obj,
            mapping.PRIMARY: None,
            mapping.IS_PRIMARY: is_primary,
            mapping.FRACTION: fraction,
            **cls._get_extension_fields(extensions),
        }

        if primary:
            r[mapping.PRIMARY] = await facet.request_bulked_get_one_class_full(
                primary, only_primary_uuid=only_primary_uuid
            )

        return r

    @classmethod
    def _get_extension_fields(cls, extensions: dict) -> dict:
        """
        Filters all but the generic attribute extension fields, and returns
        them mapped to the OS2mo data model
        :param extensions: A dict of all extensions attributes
        :return: A dict of mapped attribute extension fields
        """

        return {
            mo_key: extensions.get(lora_key)
            for mo_key, lora_key in mapping.EXTENSION_ATTRIBUTE_MAPPING
        }

    @classmethod
    async def _is_primary(
        cls, c: lora.Connector, person: str, primary: str
    ) -> bool | None:
        """
        Calculate whether a given primary class is _the_ primary class for a
        person.

        Primary classes have priorities in the "scope" field, which are
        used for ranking the classes.

        Compare the primary class to the primary classes of the other
        engagements of the person, and determine if it has the highest priority

        :param c: A LoRa connector
        :param person: The UUID of a person
        :param primary: The UUID of the primary class in question

        :return True if primary, False if not, None if functionality is disabled
        """

        if not util.get_args_flag("calculate_primary"):
            return None

        objs = [
            obj
            for _, obj in await cls._get_lora_object(c, {"tilknyttedebrugere": person})
        ]

        effect_tuples_list = [await cls._get_effects(c, obj) for obj in objs]

        # flatten and filter
        engagements = [
            effect
            for effect_tuples in effect_tuples_list
            for _, _, effect in effect_tuples
            if util.is_reg_valid(effect)
        ]

        # If only engagement
        if len(engagements) <= 1:  # pragma: no cover
            return True

        engagement_primary_uuids = [
            mapping.PRIMARY_FIELD.get_uuid(engagement) for engagement in engagements
        ]

        sorted_classes = await get_sorted_primary_class_list(c)

        for class_id, _ in sorted_classes:
            if class_id in engagement_primary_uuids:
                return class_id == primary


async def get_engagement(c: lora.Connector, uuid: UUID) -> dict[str, Any] | None:
    """
    convenience, for an often used pattern: Eagerly getting an engagement.
    :param c:
    :param uuid: uuid of engagement
    :return: First, engagement found (or None)
    """
    engagements = await EngagementReader.get(c, {"uuid": [uuid]})
    if len(engagements) == 0:  # pragma: no cover
        logger.warning("Engagement returned no results", uuid=uuid)
        return None

    if len(engagements) > 1:  # pragma: no cover
        logger.warning("Engagement returned more than one result", uuid=uuid)

    return engagements[0]
