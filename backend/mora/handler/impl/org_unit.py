# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import reading
from ... import common
from ... import exceptions
from ... import mapping
from ... import util
from ...request_scoped_globals import request_args
from ...service import orgunit

ROLE_TYPE = "org_unit"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class OrgUnitReader(reading.ReadingHandler):

    @classmethod
    async def get(cls, c, search_fields):
        object_tuples = await c.organisationenhed.get_all(**search_fields)
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c, type, objid):
        if type != "ou":
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()

        object_tuples = await c.organisationenhed.get_all_by_uuid(uuids=[objid])
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("organisationenhedegenskaber",),
            "relationer": (
                "enhedstype", "opgaver", "overordnet", "tilhoerer", "niveau"
            ),
            "tilstande": ("organisationenhedgyldighed",),
        }
        also = {}

        return await c.organisationenhed.get_effects(obj, relevant, also, **params)

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, obj_id):
        c = common.get_connector()
        only_primary_uuid = request_args.get('only_primary_uuid')

        return await orgunit.get_one_orgunit(
            c,
            obj_id,
            effect,
            details=orgunit.UnitDetails.FULL,
            validity={
                mapping.FROM: util.to_iso_date(start),
                mapping.TO: util.to_iso_date(end, is_end=True),
            },
            only_primary_uuid=only_primary_uuid
        )
