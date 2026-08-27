# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from ... import mapping
from .. import reading

ROLE_TYPE = "kle"

logger = get_logger()


@reading.register(ROLE_TYPE)
class KLEReader(reading.OrgFunkReadingHandler):
    function_key = mapping.KLE_KEY

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, funcid, flat: bool = False
    ):
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(effect)
        kle_number_uuid = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        kle_aspect_uuids = list(mapping.KLE_ASPECT_FIELD.get_uuids(effect))

        base_obj = await super()._get_mo_object_from_effect(effect, start, end, funcid)

        return {
            **base_obj,
            "org_unit_uuid": org_unit_uuid,
            "kle_number_uuid": kle_number_uuid,
            "kle_aspect_uuids": kle_aspect_uuids,
        }
