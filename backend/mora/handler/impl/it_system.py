# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""ITSystem Reading Handler (Lora)"""

from structlog import get_logger

from ... import common
from ... import exceptions
from ... import lora
from ... import mapping
from ... import util
from ...service.itsystem import MO_OBJ_TYPE
from .. import reading

ROLE_TYPE = "itsystem"

logger = get_logger()


@reading.register(ROLE_TYPE)
class ITSystemReader(reading.ReadingHandler):
    @classmethod
    async def get(cls, c, search_fields, flat: bool=False):
        object_tuples = await cls._get_lora_object(c=c, search_fields=search_fields)
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c, type, objid):  # pragma: no cover
        if type != ROLE_TYPE:
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()
        object_tuples = await c.itsystem.get_all_by_uuid(uuids=[objid])
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(cls, c, search_fields):
        if mapping.UUID in search_fields:
            return await c.itsystem.get_all_by_uuid(
                uuids=search_fields[mapping.UUID],
            )
        return await c.itsystem.get_all(**search_fields)

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("itsystemegenskaber",),
            "relationer": ("tilknyttedeorganisationer",),
            "tilstande": ("itsystemgyldighed",),
        }
        also = {}

        return await c.itsystem.get_effects(obj, relevant, also, **params)

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, obj_id, flat: bool = False
    ):
        c = common.get_connector()
        return await get_one_itsystem(
            c,
            obj_id,
            itsystem=effect,
            validity={
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(end, is_end=True),
            },
        )


async def get_one_itsystem(
    c: lora.Connector,
    itsystem_uuid,
    itsystem=None,
    only_primary_uuid: bool = False,
    validity=None,
) -> MO_OBJ_TYPE | None:
    def _get_attrs(itsystem):
        return itsystem["attributter"]["itsystemegenskaber"][0]

    if only_primary_uuid:  # pragma: no cover
        return {mapping.UUID: itsystem_uuid}

    if not itsystem:  # pragma: no cover
        # optionally exit early
        if not itsystem_uuid:
            return None

        itsystem = await c.itsystem.get(itsystem_uuid)
        if not itsystem:
            return None

    attrs = _get_attrs(itsystem)
    response = {
        "uuid": itsystem_uuid,
        "name": attrs.get("itsystemnavn"),
        "user_key": attrs.get("brugervendtnoegle"),
    }

    validities = itsystem["tilstande"]["itsystemgyldighed"]
    response[mapping.VALIDITY] = validity or util.get_effect_validity(validities[0])

    return response
