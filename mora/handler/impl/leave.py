# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from ... import mapping
from .. import reading

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

        return {
            **base_obj,
            "employee_uuid": person,
            "leave_type_uuid": leave_type,
            "engagement_uuid": engagement_uuid,
        }
