# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from typing import Any
from typing import TypeVar

from structlog import get_logger

from ... import mapping
from .. import reading

ROLE_TYPE = "related_unit"

logger = get_logger()

T = TypeVar("T")


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.RELATED_UNIT_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ) -> dict[str, Awaitable | Any]:
        org_units_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(effect)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        return {
            **base_obj,
            "org_unit_uuids": org_units_uuid,
        }
