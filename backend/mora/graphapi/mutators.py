#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------

from uuid import UUID
import strawberry
from mora.graphapi.inputs import ClassTerminationInput
from mora.graphapi.classes import terminate_class
from mora.graphapi.models import FileStore
from mora.graphapi.files import save_file
from strawberry.file_uploads import Upload
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.schema import OrganisationUnitRefresh
from mora.graphapi.org_unit import trigger_org_unit_refresh
from strawberry.file_uploads import Upload


# --------------------------------------------------------------------------------------
# Mutators
# --------------------------------------------------------------------------------------


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

    @strawberry.mutation(description="Deletes a class by UUID")
    async def class_terminate(self, input: ClassTerminationInput) -> str:
        instance = input.to_pydantic()

        return await terminate_class(uuid=instance.uuid)
