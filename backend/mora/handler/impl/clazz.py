# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Classes Reading Handler (Lora)
------------------------------

Reading handler for LoRa classes.
NOTE the file is named `clazz` to avoid conflict with the Python keyword `class`.

"""
from datetime import datetime

from structlog import get_logger

from .. import reading
from ... import common
from ... import exceptions
from ... import mapping
from ... import util
from ...service.clazz import get_one_class

logger = get_logger()

ROLE_TYPE = "class"


@reading.register(ROLE_TYPE)
class ClassReader(reading.ReadingHandler):
    @classmethod
    async def get(
        cls, c, search_fields, changed_since: datetime | None = None, flat=False
    ):
        object_tuples = await cls._get_lora_object(
            c=c, search_fields=search_fields, changed_since=changed_since
        )

        return await cls._get_obj_effects(
            c,
            object_tuples,
            is_reg_valid_fn=lambda reg: any(
                state.get("publiceret") == "Publiceret"
                for state in util.get_states(reg)
            ),
        )

    @classmethod
    async def get_from_type(cls, c, type, objid, changed_since: datetime | None = None):
        if type != ROLE_TYPE:
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()

        object_tuples = await c.facet.get_all_by_uuid(
            uuids=[objid], changed_since=changed_since
        )
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(
        cls, c, search_fields, changed_since: datetime | None = None
    ):
        if mapping.UUID in search_fields:
            return await c.klasse.get_all_by_uuid(
                uuids=search_fields[mapping.UUID],
            )
        return await c.klasse.get_all(
            changed_since=changed_since,
            **search_fields,
        )

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("klasseegenskaber",),
            "relationer": (
                "ansvarlig",
                "ejer",
            ),
            "tilstande": ("klassepubliceret",),
        }
        also = {}

        return await c.klasse.get_effects(obj, relevant, also, **params)

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, obj_id, flat: bool = False
    ):
        c = common.get_connector()
        return await get_one_class(
            c,
            obj_id,
            validity={
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(end, is_end=True),
            },
        )
