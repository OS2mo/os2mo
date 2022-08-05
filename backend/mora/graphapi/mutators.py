#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import logging
from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload

from mora.graphapi.employee import terminate_employee
from mora.graphapi.files import save_file
from mora.graphapi.inputs import EmployeeTerminationInput
from mora.graphapi.models import EmployeeTermination
from mora.graphapi.models import FileStore
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.org_unit import trigger_org_unit_refresh
from mora.graphapi.schema import OrganisationUnitRefresh
from mora.graphapi.types import EmployeeType

logger = logging.getLogger(__name__)


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Upload a file")
    async def upload_file(
        self, file_store: FileStore, file: Upload, force: bool = False
    ) -> str:
        file_name = file.filename
        file_bytes = await file.read()
        save_file(file_store, file_name, file_bytes, force)
        return "OK"

    @strawberry.mutation(description="Trigger refresh for an organisation unit")
    async def org_unit_refresh(self, uuid: UUID) -> OrganisationUnitRefresh:
        result = await trigger_org_unit_refresh(uuid)
        organisation_unit_refresh = OrganisationUnitRefreshRead(**result)
        return OrganisationUnitRefresh.from_pydantic(organisation_unit_refresh)

    @strawberry.mutation(description="Terminates an employee by UUID")
    async def employee_terminate(self, et: EmployeeTerminationInput) -> EmployeeType:
        # OBS: We do more than just 'to_pydantic()' since the method won't set
        # from_date & to_date... the input uses FakeDateTime type as default,
        # which could be the problem.
        e_terminate = EmployeeTermination(
            **et.to_pydantic().dict(exclude={"from_date", "to_date"}),
            from_date=et.from_date,
            to_date=et.to_date
        )

        return await terminate_employee(e_terminate)
