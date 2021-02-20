# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from asyncio import gather
from typing import Any, Awaitable, Dict, Iterable, TypeVar, Union

from .. import reading
from ... import mapping
from ...service import orgunit

ROLE_TYPE = "related_unit"

logger = logging.getLogger(__name__)

T = TypeVar('T')


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
        sorted_org_units = sorted(parsed_org_units, key=lambda x: x.get('name'))
        return sorted_org_units

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end,
                                         funcid) -> Dict[str, Union[Awaitable, Any]]:
        org_units = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuids(effect)

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)
        # only_primary_uuid = flask.request.args.get('only_primary_uuid')
        only_primary_uuid = False

        org_unit_awaitables = [
            await orgunit.request_bulked_get_one_orgunit(
                unitid=org_unit_uuid,
                details=orgunit.UnitDetails.MINIMAL,
                only_primary_uuid=only_primary_uuid
            )
            for org_unit_uuid in org_units]

        r = {
            **base_obj,
            mapping.ORG_UNIT: cls.get_sorted_org_units(org_unit_awaitables),
        }

        return r
