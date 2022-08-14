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
from strawberry.types import Info

from mora.graphapi.inputs import OrganizationUnitTerminateInput
from mora.graphapi.models import FileStore
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.org_unit import terminate_org_unit
from mora.graphapi.org_unit import trigger_org_unit_refresh
from mora.graphapi.schema import OrganisationUnitRefresh
from mora.graphapi.types import EngagementTerminateType
from mora.graphapi.types import OrganizationUnit

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
