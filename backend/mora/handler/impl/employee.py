# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from structlog import get_logger
from datetime import datetime
from typing import Any, Dict, Optional

from .. import reading
from ... import common, exceptions, mapping, util
from ...lora import Connector
from ...service import employee

ROLE_TYPE = "employee"

logger = get_logger()


@reading.register(ROLE_TYPE)
class EmployeeReader(reading.ReadingHandler):
    @classmethod
    async def get(
        cls,
        c: Connector,
        search_fields: Dict[Any, Any],
        changed_since: Optional[datetime] = None,
    ):
        object_tuples = await cls._get_lora_object(
            c=c, search_fields=search_fields, changed_since=changed_since
        )
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(
        cls, c: Connector, type: str, objid, changed_since: Optional[datetime] = None
    ):
        if type != "e":
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()

        object_tuples = await c.bruger.get_all_by_uuid(
            uuids=[objid], changed_since=changed_since
        )
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(
        cls, c, search_fields, changed_since: Optional[datetime] = None
    ):
        if mapping.UUID in search_fields:
            return await c.bruger.get_all_by_uuid(
                uuids=search_fields[mapping.UUID],
                changed_since=changed_since,
            )
        return await c.bruger.get_all(
            changed_since=changed_since,
            **search_fields,
        )

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("brugeregenskaber", "brugerudvidelser"),
            "relationer": ("tilknyttedepersoner", "tilhoerer"),
            "tilstande": ("brugergyldighed",),
        }

        return await c.bruger.get_effects(obj, relevant, {}, **params)

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, obj_id):
        c = common.get_connector()
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        employee_object = await employee.get_one_employee(
            c,
            obj_id,
            effect,
            details=employee.EmployeeDetails.FULL,
            only_primary_uuid=only_primary_uuid,
        )

        employee_object["validity"] = {
            mapping.FROM: util.to_iso_date(start),
            mapping.TO: util.to_iso_date(end, is_end=True),
        }

        return employee_object
