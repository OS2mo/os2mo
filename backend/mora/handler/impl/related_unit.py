# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from collections.abc import Awaitable
from collections.abc import Iterable
from typing import Any
from typing import TypeVar

from structlog import get_logger

from .. import reading
from ... import mapping
from ...graphapi.middleware import is_graphql
from ...service import orgunit
from mora import util

ROLE_TYPE = "related_unit"

logger = get_logger()

T = TypeVar("T")


@reading.register(ROLE_TYPE)
class RoleReader(reading.OrgFunkReadingHandler):
    function_key = mapping.RELATED_UNIT_KEY

    @staticmethod
    async def get_sorted_org_units(aws: Iterable[Awaitable[T]]) -> T:
        """
        wrapper to allow delayed sort after gather
        :param aws:
        :return:
        """

        parsed_org_units = await gather(*aws)
        sorted_org_units = sorted(parsed_org_units, key=lambda x: x.get("name"))
        return sorted_org_units

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ) -> dict[str, Awaitable | Any]:
        org_units_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(effect)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)
        if is_graphql():
            return {
                **base_obj,
                "org_unit_uuids": org_units_uuid,
            }

        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        org_unit_awaitables = [
            await orgunit.request_bulked_get_one_orgunit(
                unitid=org_unit_uuid,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid,
            )
            for org_unit_uuid in org_units_uuid
        ]

        r = {
            **base_obj,
            mapping.ORG_UNIT: cls.get_sorted_org_units(org_unit_awaitables),
        }

        return r
