# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from mora import util

from ... import mapping
from ...graphapi.middleware import is_graphql
from ...service import facet
from ...service import orgunit
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

        if is_graphql():
            return {
                **base_obj,
                "org_unit_uuid": org_unit_uuid,
                "kle_number_uuid": kle_number_uuid,
                "kle_aspect_uuids": kle_aspect_uuids,
            }

        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        kle_aspect = [
            await facet.request_bulked_get_one_class_full(
                obj_uuid, only_primary_uuid=only_primary_uuid
            )
            for obj_uuid in kle_aspect_uuids
        ]

        kle_number = await facet.request_bulked_get_one_class_full(
            kle_number_uuid, only_primary_uuid=only_primary_uuid
        )

        org_unit = await orgunit.request_bulked_get_one_orgunit(
            org_unit_uuid,
            details=orgunit.UnitDetails.MINIMAL,
            only_primary_uuid=only_primary_uuid,
        )

        r = {
            **base_obj,
            mapping.KLE_ASPECT: kle_aspect,
            mapping.KLE_NUMBER: kle_number,
            mapping.ORG_UNIT: org_unit,
        }

        return r
