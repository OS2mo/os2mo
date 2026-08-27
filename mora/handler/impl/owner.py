# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from ... import mapping
from ...common import parse_owner_inference_priority_str
from ...mapping import EXTENSION_1
from .. import reading

ROLE_TYPE = mapping.OWNER

logger = get_logger()


@reading.register(ROLE_TYPE)
class OwnerReader(reading.OrgFunkReadingHandler):
    function_key = mapping.OWNER

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        owned_person = mapping.USER_FIELD.get_uuid(effect)
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        owner_uuid = mapping.EMPLOYEE_PERSON_FIELD.get_uuid(effect)
        extensions = mapping.ORG_FUNK_UDVIDELSER_FIELD(effect)
        extensions = extensions[0] if extensions else {}
        inference_priority_str = extensions.get(EXTENSION_1, None)
        if inference_priority_str:  # filters both None and empty string
            # Validate the priority string; raises on invalid input
            parse_owner_inference_priority_str(inference_priority_str)
        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        return {
            **base_obj,
            "owner_uuid": owner_uuid,
            "employee_uuid": owned_person,
            "org_unit_uuid": org_unit,
            "owner_inference_priority": inference_priority_str,
        }
