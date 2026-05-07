# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Classes Reading Handler (Lora)
------------------------------

Reading handler for LoRa classes.
NOTE the file is named `clazz` to avoid conflict with the Python keyword `class`.

"""

from structlog import get_logger

from mora.service.facet import get_one_class

from ... import common
from ... import exceptions
from ... import lora
from ... import mapping
from ... import util
from .. import reading

logger = get_logger()

ROLE_TYPE = "class"


def is_class_reg_valid(reg) -> bool:
    return any(
        state.get("publiceret") == "Publiceret" for state in util.get_states(reg)
    )


@reading.register(ROLE_TYPE)
class ClassReader(reading.ReadingHandler):
    is_reg_valid = is_class_reg_valid

    @classmethod
    async def get(cls, c: lora.Connector, search_fields, flat=False):
        object_tuples = await cls._get_lora_object(c=c, search_fields=search_fields)
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c: lora.Connector, type, objid):  # pragma: no cover
        if type != ROLE_TYPE:
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()
        object_tuples = await c.klasse.get_all_by_uuid(uuids=[objid])
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(cls, c: lora.Connector, search_fields):
        if mapping.UUID in search_fields:
            return await c.klasse.get_all_by_uuid(
                uuids=search_fields[mapping.UUID],
                registration_time=search_fields.get("registration_time"),
            )
        return await c.klasse.get_all(**search_fields)

    @classmethod
    async def _get_effects(cls, c: lora.Connector, obj, **params):
        relevant = {
            "attributter": ("klasseegenskaber",),
            "relationer": (
                "ansvarlig",
                "ejer",
                "facet",
                "mapninger",
                "overordnetklasse",
            ),
            "tilstande": ("klassepubliceret",),
        }
        also = {}
        return await c.klasse.get_effects(obj, relevant, also, **params)

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, obj_id, flat: bool = False
    ):
        return await get_one_class(
            common.get_connector(),
            obj_id,
            clazz=effect,
            extended=True,
            validity={
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(end, is_end=True),
            },
        )
