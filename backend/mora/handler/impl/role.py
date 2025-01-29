# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import HTTPException
from structlog import get_logger

from ... import mapping
from ...graphapi.middleware import is_graphql
from .. import reading

ROLE_TYPE = "rolebinding"

logger = get_logger()


@reading.register(ROLE_TYPE)
class RoleBindingReader(reading.OrgFunkReadingHandler):
    function_key = mapping.ROLEBINDING_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        role_uuid = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        it_user_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        if is_graphql():
            return {
                **base_obj,
                "org_unit_uuid": org_unit_uuid,
                "role": role_uuid,
                "it_user_uuid": it_user_uuid,
            }

        raise HTTPException(
            status_code=404, detail="Role/bindings are only available through GraphQL."
        )
