# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger

from ... import common
from ... import exceptions
from ... import mapping
from ... import util
from ...service import facet
from .. import reading

ROLE_TYPE = "facet"

logger = get_logger()


def is_facet_reg_valid(reg) -> bool:
    return any(
        state.get("publiceret") == "Publiceret" for state in util.get_states(reg)
    )


@reading.register(ROLE_TYPE)
class FacetReader(reading.ReadingHandler):
    is_reg_valid = is_facet_reg_valid

    @classmethod
    async def get(cls, c, search_fields, flat=False):
        object_tuples = await cls._get_lora_object(c=c, search_fields=search_fields)
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c, type, objid):
        if type != ROLE_TYPE:
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()
        object_tuples = await c.facet.get_all_by_uuid(uuids=[objid])
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(cls, c, search_fields):
        if mapping.UUID in search_fields:
            return await c.facet.get_all_by_uuid(uuids=search_fields[mapping.UUID])
        return await c.facet.get_all(**search_fields)

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("facetegenskaber",),
            "relationer": ("ansvarlig", "ejer", "facettilhoerer"),
            "tilstande": ("facetpubliceret",),
        }
        also = {}
        return await c.facet.get_effects(obj, relevant, also, **params)

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, obj_id, flat: bool = False
    ):
        return await facet.get_one_facet(
            common.get_connector(),
            obj_id,
            facet=effect,
            extended=True,
            validity={
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(end, is_end=True),
            },
        )
