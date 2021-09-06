# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Dict

from fastapi.encoders import jsonable_encoder
from mora.handler import reading
from mora.handler.impl import employee
from mora.handler.impl import org_unit
from pydantic import BaseModel


def instance2dict(instance: BaseModel) -> Dict:
    """Convert a pydantic model to a jsonable dictionary.

    Args:
        instance: Instance to be converted.

    Returns:
        Dictionary which could be converted to json using json.dumps
    """
    return jsonable_encoder(instance.dict(by_alias=True))


def reader_to_endpoint(reader: reading.ReadingHandler):
    return {
        employee.EmployeeReader: "employee",
        org_unit.OrgUnitReader: "org_unit",
    }[reader]
