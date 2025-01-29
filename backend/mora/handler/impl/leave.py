# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from mora import lora
from mora import util

from ... import mapping
from ...graphapi.middleware import is_graphql
from ...service import employee
from ...service import facet
from .. import reading
from .engagement import get_engagement

ROLE_TYPE = "leave"

logger = get_logger()


@reading.register(ROLE_TYPE)
class LeaveReader(reading.OrgFunkReadingHandler):
    function_key = mapping.LEAVE_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        person = mapping.USER_FIELD.get_uuid(effect)
        leave_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        engagement_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        if is_graphql():
            return {
                **base_obj,
                "employee_uuid": person,
                "leave_type_uuid": leave_type,
                "engagement_uuid": engagement_uuid,
            }

        person_obj = await employee.request_bulked_get_one_employee(
            person, only_primary_uuid=only_primary_uuid
        )

        leave_type_obj = await facet.request_bulked_get_one_class(
            leave_type, only_primary_uuid=only_primary_uuid
        )

        if only_primary_uuid:
            engagement = {mapping.UUID: engagement_uuid}
        else:
            # We look up whatever engagement is active at the present time period
            # to account for edge cases where the engagement might have changed or is
            # no longer active during the time period
            present_connector = lora.Connector(validity="present")
            engagement = await get_engagement(present_connector, uuid=engagement_uuid)

        r = {
            **base_obj,
            mapping.PERSON: person_obj,
            mapping.LEAVE_TYPE: leave_type_obj,
            mapping.ENGAGEMENT: engagement,
        }

        return r
