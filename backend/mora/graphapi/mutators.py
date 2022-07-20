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
        try:
            if not await terminate_org_unit(unit):
                raise Exception(
                    "Unable to terminate organization unit, due to an unknown error."
                )

            return OrganizationUnit(uuid=unit.uuid)
        except Exception as e:
            logger.exception('Error occured while running "terminate_org_unit()".')
            raise e
