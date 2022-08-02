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

from mora.graphapi.files import save_file
from mora.graphapi.inputs import OrganizationUnitTerminateInput
from mora.graphapi.models import FileStore
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.org_unit import terminate_org_unit
from mora.graphapi.org_unit import trigger_org_unit_refresh
from mora.graphapi.schema import OrganisationUnitRefresh
from mora.graphapi.types import OrganizationUnit

logger = logging.getLogger(__name__)
from typing import Union
from uuid import UUID

import strawberry
from pydantic import ValidationError
from strawberry.file_uploads import Upload

from .models import FileStore
from mora.graphapi.files import save_file
from mora.graphapi.inputs import ITSystemInput
from mora.graphapi.it_systems import upsert_it_system
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.org_unit import trigger_org_unit_refresh
from mora.graphapi.schema import ITSystem
from mora.graphapi.schema import OrganisationUnitRefresh
from mora.graphapi.types import GenericError

# --------------------------------------------------------------------------------------
# Graphapi mutators
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

    @strawberry.mutation(description="Terminates an organization unit by UUID")
    async def org_unit_terminate(
        self, unit: OrganizationUnitTerminateInput
    ) -> OrganizationUnit:
        return await terminate_org_unit(unit.to_pydantic())

    @strawberry.mutation(description="Create new it system")
    async def create_it_system(
        self, input: ITSystemInput
    ) -> Union[ITSystem, GenericError]:

        try:
            instance = input.to_pydantic()

            return await upsert_it_system(
                uuid=instance.uuid,
                type_=instance.type_,
                name=instance.name,
                user_key=instance.user_key,
            )

        except ValidationError as e:
            return GenericError(error_message=(str(e)))
