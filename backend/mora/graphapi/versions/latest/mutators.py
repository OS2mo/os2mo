# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from .address import create as create_address
from .address import terminate_addr
from .address import update_address
from .association import create_association
from .association import terminate_association
from .association import update_association
from .classes import create_class
from .employee import create as employee_create
from .employee import terminate as terminate_employee
from .employee import update as employee_update
from .engagements import create_engagement
from .engagements import terminate_engagement
from .engagements import update_engagement
from .facets import create_facet
from .inputs import AddressCreateInput
from .inputs import AddressTerminateInput
from .inputs import AddressUpdateInput
from .inputs import AssociationCreateInput
from .inputs import AssociationTerminateInput
from .inputs import AssociationUpdateInput
from .inputs import ClassCreateInput
from .inputs import EmployeeCreateInput
from .inputs import EmployeeTerminateInput
from .inputs import EmployeeUpdateInput
from .inputs import EngagementCreateInput
from .inputs import EngagementTerminateInput
from .inputs import EngagementUpdateInput
from .inputs import FacetCreateInput
from .inputs import ITUserCreateInput
from .inputs import ITUserTerminateInput
from .inputs import ITUserUpdateInput
from .inputs import ManagerCreateInput
from .inputs import ManagerTerminateInput
from .inputs import ManagerUpdateInput
from .inputs import OrganisationUnitCreateInput
from .inputs import OrganisationUnitTerminateInput
from .inputs import OrganisationUnitUpdateInput
from .it_user import create as create_ituser
from .it_user import terminate as terminate_ituser
from .it_user import update as update_ituser
from .manager import create_manager
from .manager import terminate_manager
from .manager import update_manager
from .models import FileStore
from .models import OrganisationUnitRefreshRead
from .org_unit import create_org_unit
from .org_unit import terminate_org_unit
from .org_unit import trigger_org_unit_refresh
from .org_unit import update_org_unit
from .permissions import gen_role_permission
from .schema import OrganisationUnitRefresh
from .types import AddressCreateType
from .types import AddressTerminateType
from .types import AddressType
from .types import AssociationType
from .types import EmployeeType
from .types import EmployeeUpdateResponseType
from .types import EngagementTerminateType
from .types import EngagementType
from .types import ITUserType
from .types import ManagerType
from .types import OrganisationUnitType
from .types import UUIDReturn
from mora.common import get_connector

logger = logging.getLogger(__name__)

# NOTE: The end goal is not to require admin for all GraphQL mutators, but rather to
# have unique roles for each mutator.
# The current solution is merely to stop unauthorized access to writing.
# TODO: Implement proper permissions
admin_permission_class = gen_role_permission("admin", force_permission_check=True)


@strawberry.type
class Mutation:
    # Addresses
    # ---------
    @strawberry.mutation(
        description="Create an address.",
        permission_classes=[admin_permission_class],
    )
    async def address_create(self, input: AddressCreateInput) -> AddressCreateType:
        return await create_address(input.to_pydantic())

    @strawberry.mutation(
        description="Updates an address.",
        permission_classes=[admin_permission_class],
    )
    async def address_update(self, input: AddressUpdateInput) -> AddressType:
        return await update_address(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an address by UUID",
        permission_classes=[admin_permission_class],
    )
    async def address_terminate(
        self, at: AddressTerminateInput
    ) -> AddressTerminateType:
        return await terminate_addr(at.to_pydantic())

    @strawberry.mutation(
        description="Delete an address.",
        permission_classes=[admin_permission_class],
    )
    async def address_delete(self, uuid: UUID) -> "DeleteResponse":
        return await delete_organisationfunktion(uuid)

    # Associations
    # ------------
    @strawberry.mutation(
        description="Creates an association.",
        permission_classes=[admin_permission_class],
    )
    async def association_create(
        self, input: AssociationCreateInput
    ) -> AssociationType:
        return await create_association(input.to_pydantic())

    @strawberry.mutation(
        description="Updates an association.",
        permission_classes=[admin_permission_class],
    )
    async def association_update(
        self, input: AssociationUpdateInput
    ) -> AssociationType:
        return await update_association(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an association by UUID",
        permission_classes=[admin_permission_class],
    )
    async def association_terminate(
        self, input: AssociationTerminateInput
    ) -> AssociationType:
        return await terminate_association(input.to_pydantic())

    # TODO: association_delete

    # Classes
    # -------
    @strawberry.mutation(
        description="Create new mo-class under facet",
        permission_classes=[admin_permission_class],
    )
    async def class_create(self, input: ClassCreateInput) -> UUIDReturn:
        return await create_class(input.to_pydantic())

    # TODO: class_update
    # TODO: class_terminate
    # TODO: class_delete

    # Employees
    # ---------
    @strawberry.mutation(
        description="Creates an employee for a specific organisation.",
        permission_classes=[admin_permission_class],
    )
    async def employee_create(self, input: EmployeeCreateInput) -> EmployeeType:
        return await employee_create(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an employee by UUID",
        permission_classes=[admin_permission_class],
    )
    async def employee_update(
        self, input: EmployeeUpdateInput
    ) -> EmployeeUpdateResponseType:
        return await employee_update(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an employee by UUID",
        permission_classes=[admin_permission_class],
    )
    async def employee_terminate(self, input: EmployeeTerminateInput) -> EmployeeType:
        return await terminate_employee(input.to_pydantic())

    # TODO: employee_delete

    # Engagements
    # -----------
    @strawberry.mutation(
        description="Create an engagement", permission_classes=[admin_permission_class]
    )
    async def engagement_create(self, input: EngagementCreateInput) -> EngagementType:
        return await create_engagement(input.to_pydantic())

    @strawberry.mutation(
        description="Updates an engagement by UUID",
        permission_classes=[admin_permission_class],
    )
    async def engagement_update(self, input: EngagementUpdateInput) -> EngagementType:
        return await update_engagement(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an engagement by UUID",
        permission_classes=[admin_permission_class],
    )
    async def engagement_terminate(
        self, input: EngagementTerminateInput
    ) -> EngagementTerminateType:
        return await terminate_engagement(input.to_pydantic())

    @strawberry.mutation(
        description="Delete an engagement.",
        permission_classes=[admin_permission_class],
    )
    async def engagement_delete(self, uuid: UUID) -> "DeleteResponse":
        return await delete_organisationfunktion(uuid)

    # EngagementsAssociations
    # -----------------------

    # TODO: engagement_association_create
    # TODO: engagement_association_update
    # TODO: engagement_association_terminate
    # TODO: engagement_association_delete

    # Facets
    # ------
    @strawberry.mutation(
        description="Create new facet object",
        permission_classes=[admin_permission_class],
    )
    async def facet_create(self, input: FacetCreateInput) -> UUIDReturn:
        return await create_facet(input.to_pydantic())

    # TODO: facet_update
    # TODO: facet_terminate
    # TODO: facet_delete

    # ITSystems
    # ---------

    # TODO: itsystem_create
    # TODO: itsystem_update
    # TODO: itsystem_terminate
    # TODO: itsystem_delete

    # ITUsers
    # -------
    @strawberry.mutation(
        description="Creates an IT-User.",
        permission_classes=[admin_permission_class],
    )
    async def ituser_create(self, input: ITUserCreateInput) -> ITUserType:
        return await create_ituser(input.to_pydantic())

    @strawberry.mutation(
        description="Updates an IT-User.",
        permission_classes=[admin_permission_class],
    )
    async def ituser_update(self, input: ITUserUpdateInput) -> ITUserType:
        return await update_ituser(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates IT-user by UUID",
        permission_classes=[admin_permission_class],
    )
    async def ituser_terminate(self, input: ITUserTerminateInput) -> ITUserType:
        return await terminate_ituser(input.to_pydantic())

    @strawberry.mutation(
        description="Delete an IT-User.",
        permission_classes=[admin_permission_class],
    )
    async def ituser_delete(self, uuid: UUID) -> "DeleteResponse":
        return await delete_organisationfunktion(uuid)

    # KLEs
    # ----

    # TODO: kle_create
    # TODO: kle_update
    # TODO: kle_terminate
    # TODO: kle_delete

    # Leave
    # -----

    # TODO: leave_create
    # TODO: leave_update
    # TODO: leave_terminate
    # TODO: leave_delete

    # Managers
    # --------

    @strawberry.mutation(
        description="Creates a manager for a specific organisation.",
        permission_classes=[admin_permission_class],
    )
    async def manager_create(self, input: ManagerCreateInput) -> ManagerType:
        return await create_manager(input.to_pydantic())

    @strawberry.mutation(
        description="Updates a manager for a specific organisation by UUID.",
        permission_classes=[admin_permission_class],
    )
    async def manager_update(self, input: ManagerUpdateInput) -> ManagerType:
        return await update_manager(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates a manager unit by UUID",
        permission_classes=[admin_permission_class],
    )
    async def manager_terminate(self, input: ManagerTerminateInput) -> ManagerType:
        return await terminate_manager(input.to_pydantic())

    # TODO: manager_delete

    # Root Organisation
    # -----------------

    # TODO: org_create
    # TODO: org_update
    # TODO: org_terminate
    # TODO: org_delete

    # Organisational Units
    # --------------------
    @strawberry.mutation(
        description="Trigger refresh for an organisation unit",
        permission_classes=[admin_permission_class],
    )
    async def org_unit_refresh(self, uuid: UUID) -> OrganisationUnitRefresh:
        result = await trigger_org_unit_refresh(uuid)
        organisation_unit_refresh = OrganisationUnitRefreshRead(**result)
        return OrganisationUnitRefresh.from_pydantic(organisation_unit_refresh)

    @strawberry.mutation(
        description="Creates org-unit",
        permission_classes=[admin_permission_class],
    )
    async def org_unit_create(
        self, input: OrganisationUnitCreateInput
    ) -> OrganisationUnitType:
        return await create_org_unit(input.to_pydantic())

    @strawberry.mutation(
        description="Updates an organisation unit for a specific organisation by UUID.",
        permission_classes=[admin_permission_class],
    )
    async def org_unit_update(
        self, input: OrganisationUnitUpdateInput
    ) -> OrganisationUnitType:
        return await update_org_unit(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an organization unit by UUID",
        permission_classes=[admin_permission_class],
    )
    async def org_unit_terminate(
        self, unit: OrganisationUnitTerminateInput
    ) -> OrganisationUnitType:
        return await terminate_org_unit(unit.to_pydantic())

    # TODO: org_unit_delete

    # Related Units
    # -------------

    # TODO: related_create
    # TODO: related_update
    # TODO: related_terminate
    # TODO: related_delete

    # Roles
    # -----

    # TODO: roles_create
    # TODO: roles_update
    # TODO: roles_terminate
    # TODO: roles_delete

    # Files
    # -----
    @strawberry.mutation(
        description="Upload a file",
        permission_classes=[admin_permission_class],
    )
    async def upload_file(
        self, info: Info, file_store: FileStore, file: Upload, force: bool = False
    ) -> str:
        filestorage = info.context["filestorage"]

        file_name = file.filename
        file_bytes = await file.read()
        filestorage.save_file(file_store, file_name, file_bytes, force)
        return "OK"


@strawberry.type
class DeleteResponse:
    uuid: UUID


async def delete_organisationfunktion(uuid: UUID) -> DeleteResponse:
    """Delete an organisationfunktion by creating a "Slettet" (deleted) registration."""
    c = get_connector()
    lora_response = await c.organisationfunktion.delete(uuid)
    return DeleteResponse(uuid=lora_response)
