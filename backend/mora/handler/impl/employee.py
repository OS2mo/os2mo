# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from structlog import get_logger

from ... import common
from ... import exceptions
from ... import mapping
from ... import util
from ...graphapi.middleware import is_graphql
from ...lora import Connector
from ...service import employee
from .. import reading

ROLE_TYPE = "employee"

logger = get_logger()


@reading.register(ROLE_TYPE)
class EmployeeReader(reading.ReadingHandler):
    @classmethod
    async def get(
        cls,
        c: Connector,
        search_fields: dict[Any, Any],
        flat: bool = False,
    ):
        object_tuples = await cls._get_lora_object(c=c, search_fields=search_fields)
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def get_from_type(cls, c: Connector, type: str, objid):  # pragma: no cover
        if type != "e":
            exceptions.ErrorCodes.E_INVALID_ROLE_TYPE()

        object_tuples = await c.bruger.get_all_by_uuid(uuids=[objid])
        return await cls._get_obj_effects(c, object_tuples)

    @classmethod
    async def _get_lora_object(cls, c, search_fields):
        if mapping.UUID in search_fields:
            return await c.bruger.get_all_by_uuid(
                uuids=search_fields[mapping.UUID],
                registration_time=search_fields.get("registration_time"),
            )
        return await c.bruger.get_all(**search_fields)

    @classmethod
    async def _get_effects(cls, c, obj, **params):
        relevant = {
            "attributter": ("brugeregenskaber", "brugerudvidelser"),
            "relationer": ("tilknyttedepersoner", "tilhoerer"),
            "tilstande": ("brugergyldighed",),
        }

        return await c.bruger.get_effects(obj, relevant, {}, **params)

    @classmethod
    async def _get_mo_object_from_effect(
        cls, effect, start, end, obj_id, flat: bool = False
    ):
        c = common.get_connector()
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        details = employee.EmployeeDetails.FULL
        if is_graphql():
            details = employee.EmployeeDetails.MINIMAL

        employee_object = await employee.get_one_employee(
            c,
            obj_id,
            effect,
            details=details,
            only_primary_uuid=only_primary_uuid,
        )

        employee_object["validity"] = {
            mapping.FROM: util.to_iso_date(start),
            mapping.TO: util.to_iso_date(end, is_end=True),
        }

        return employee_object
