#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from mora import mapping
from mora.graphapi.models import EmployeeCreate
from mora.graphapi.types import EmployeeType
from mora.service.employee import EmployeeRequestHandler


async def create(ec: EmployeeCreate) -> EmployeeType:
    # Convert data model to dict to fit into existing logic
    req_dict = ec.dict(by_alias=True)
    req_dict[mapping.ORG][mapping.UUID] = str(req_dict[mapping.ORG][mapping.UUID])

    # Copied service-logic
    request = await EmployeeRequestHandler.construct(
        req_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return EmployeeType(uuid=UUID(uuid))
