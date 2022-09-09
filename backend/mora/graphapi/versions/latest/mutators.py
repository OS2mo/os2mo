# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from .address import terminate_addr
from .employee import create as employee_create
from .employee import terminate as terminate_employee
from .employee import update as employee_update
from .engagements import terminate_engagement
from .inputs import AddressTerminateInput
from .inputs import EmployeeCreateInput
from .inputs import EmployeeTerminateInput
from .inputs import EmployeeUpdateInput
from .inputs import EngagementTerminateInput
from .inputs import OrganizationUnitTerminateInput
from .models import FileStore
from .models import OrganisationUnitRefreshRead
from .org_unit import terminate_org_unit
from .org_unit import trigger_org_unit_refresh
from .schema import OrganisationUnitRefresh
from .types import AddressTerminateType
from .types import EmployeeType
from .types import EngagementTerminateType
from .types import OrganizationUnit

logger = logging.getLogger(__name__)


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Upload a file")
    async def upload_file(
        self, info: Info, file_store: FileStore, file: Upload, force: bool = False
    ) -> str:
        filestorage = info.context["filestorage"]

        file_name = file.filename
        file_bytes = await file.read()
        filestorage.save_file(file_store, file_name, file_bytes, force)
        return "OK"

    @strawberry.mutation(description="Trigger refresh for an organisation unit")
    async def org_unit_refresh(self, uuid: UUID) -> OrganisationUnitRefresh:
        result = await trigger_org_unit_refresh(uuid)
        organisation_unit_refresh = OrganisationUnitRefreshRead(**result)
        return OrganisationUnitRefresh.from_pydantic(organisation_unit_refresh)

    @strawberry.mutation(description="Terminates an organization unit by UUID")
    async def org_unit_terminate(
        self, unit: OrganizationUnitTerminateInput
    ) -> OrganizationUnit:
        return await terminate_org_unit(unit.to_pydantic())

    @strawberry.mutation(description="Terminates an engagement by UUID")
    async def engagement_terminate(
        self, unit: EngagementTerminateInput
    ) -> EngagementTerminateType:
        return await terminate_engagement(unit.to_pydantic())

    @strawberry.mutation(description="Terminates an address by UUID")
    async def address_terminate(
        self, at: AddressTerminateInput
    ) -> AddressTerminateType:
        return await terminate_addr(at.to_pydantic())

    @strawberry.mutation(description="Creates an employee for a specific organisation.")
    async def employee_create(self, input: EmployeeCreateInput) -> EmployeeType:
        return await employee_create(input.to_pydantic())

    @strawberry.mutation(description="Terminates an employee by UUID")
    async def employee_terminate(self, input: EmployeeTerminateInput) -> EmployeeType:
        return await terminate_employee(input.to_pydantic())

    @strawberry.mutation(description="Terminates an employee by UUID")
    async def employee_update(self, input: EmployeeUpdateInput) -> EmployeeType:
        return await employee_update(input.to_pydantic())