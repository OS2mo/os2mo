# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from .address import create as create_addr
from .address import terminate as terminate_addr
from .association import create_association
from .classes import create_class
from .employee import create as employee_create
from .employee import terminate as terminate_employee
from .employee import update as employee_update
from .engagements import create_engagement
from .engagements import terminate_engagement
from .facets import create_facet
from .inputs import AddressCreateInput
from .inputs import AddressTerminateInput
from .inputs import AssociationCreateInput
from .inputs import ClassCreateInput
from .inputs import EmployeeCreateInput
from .inputs import EmployeeTerminateInput
from .inputs import EmployeeUpdateInput
from .inputs import EngagementCreateInput
from .inputs import EngagementTerminateInput
from .inputs import FacetCreateInput
from .inputs import ITUserCreateInput
from .inputs import ITUserTerminateInput
from .inputs import ITUserUpdateInput
from .inputs import ManagerCreateInput
from .inputs import OrganizationUnitCreateInput
from .inputs import OrganizationUnitTerminateInput
from .it_user import create as create_ituser
from .it_user import terminate as terminate_ituser
from .it_user import update as update_ituser
from .manager import create_manager
from .models import FileStore
from .models import OrganisationUnitRefreshRead
from .org_unit import create_org_unit
from .org_unit import terminate_org_unit
from .org_unit import trigger_org_unit_refresh
from .permissions import gen_role_permission
from .schema import OrganisationUnitRefresh
from .types import AddressCreateType
from .types import AddressTerminateType
from .types import AssociationType
from .types import ClassCreateType
from .types import EmployeeType
from .types import EngagementTerminateType
from .types import EngagementType
from .types import FacetType
from .types import ITUserType
from .types import ManagerType
from .types import OrganizationUnit

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
        description="Create an address",
        permission_classes=[admin_permission_class],
    )
    async def address_create(self, input: AddressCreateInput) -> AddressCreateType:
        # We use "type: ignore" to prevent mypy+strawberry pre-commit fails
        return await create_addr(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Terminates an address by UUID",
        permission_classes=[admin_permission_class],
    )
    async def address_terminate(
        self, at: AddressTerminateInput
    ) -> AddressTerminateType:
        return await terminate_addr(at.to_pydantic())  # type: ignore

    # Associations
    # ------------
    @strawberry.mutation(
        description="Creates an association.",
        permission_classes=[admin_permission_class],
    )
    async def association_create(
        self, input: AssociationCreateInput
    ) -> AssociationType:
        # Have to use type:ignore for now due to:
        # * https://github.com/strawberry-graphql/strawberry/pull/2017
        return await create_association(input.to_pydantic())  # type: ignore

    # Classes
    # -------
    @strawberry.mutation(
        description="Create new mo-class under facet",
        permission_classes=[admin_permission_class],
    )
    async def class_create(self, input: ClassCreateInput) -> ClassCreateType:

        return await create_class(input.to_pydantic())  # type: ignore

    # Employees
    # ---------
    @strawberry.mutation(
        description="Creates an employee for a specific organisation.",
        permission_classes=[admin_permission_class],
    )
    async def employee_create(self, input: EmployeeCreateInput) -> EmployeeType:
        # Have to use type:ignore for now due to:
        # * https://github.com/strawberry-graphql/strawberry/pull/2017
        return await employee_create(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Terminates an employee by UUID",
        permission_classes=[admin_permission_class],
    )
    async def employee_update(self, input: EmployeeUpdateInput) -> EmployeeType:
        return await employee_update(input.to_pydantic())

    @strawberry.mutation(
        description="Terminates an employee by UUID",
        permission_classes=[admin_permission_class],
    )
    async def employee_terminate(self, input: EmployeeTerminateInput) -> EmployeeType:
        return await terminate_employee(input.to_pydantic())  # type: ignore

    # Engagements
    # -----------
    @strawberry.mutation(
        description="Create an engagement", permission_classes=[admin_permission_class]
    )
    async def engagement_create(self, input: EngagementCreateInput) -> EngagementType:
        # Have to use type:ignore for now due to:
        # * https://github.com/strawberry-graphql/strawberry/pull/2017
        return await create_engagement(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Terminates an engagement by UUID",
        permission_classes=[admin_permission_class],
    )
    async def engagement_terminate(
        self, unit: EngagementTerminateInput
    ) -> EngagementTerminateType:
        return await terminate_engagement(unit.to_pydantic())  # type: ignore

    # EngagementsAssociations
    # -----------------------

    # Facets
    # ------
    @strawberry.mutation(
        description="Create new facet object",
        permission_classes=[admin_permission_class],
    )
    async def facet_create(self, input: FacetCreateInput) -> FacetType:
        return await create_facet(input.to_pydantic())  # type: ignore

    # ITSystems
    # ---------

    # ITUsers
    # -------
    @strawberry.mutation(
        description="Creates an IT-User.",
        permission_classes=[admin_permission_class],
    )
    async def ituser_create(self, input: ITUserCreateInput) -> ITUserType:
        return await create_ituser(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Terminates IT-user by UUID",
        permission_classes=[admin_permission_class],
    )
    async def ituser_terminate(self, input: ITUserTerminateInput) -> ITUserType:
        return await terminate_ituser(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Updates an IT-User.",
        permission_classes=[admin_permission_class],
    )
    async def ituser_update(self, input: ITUserUpdateInput) -> ITUserType:
        return await update_ituser(input.to_pydantic())  # type: ignore

    # KLEs
    # ----

    # Leave
    # -----

    # Managers
    # --------
    @strawberry.mutation(
        description="Creates a manager for a specific organisation.",
        permission_classes=[admin_permission_class],
    )
    async def manager_create(self, input: ManagerCreateInput) -> ManagerType:
        return await create_manager(input.to_pydantic())  # type: ignore

    # Root Organisation
    # -----------------

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
        self, input: OrganizationUnitCreateInput
    ) -> OrganizationUnit:
        # Have to use type:ignore for now due to:
        # * https://github.com/strawberry-graphql/strawberry/pull/2017
        return await create_org_unit(input.to_pydantic())  # type: ignore

    @strawberry.mutation(
        description="Terminates an organization unit by UUID",
        permission_classes=[admin_permission_class],
    )
    async def org_unit_terminate(
        self, unit: OrganizationUnitTerminateInput
    ) -> OrganizationUnit:
        return await terminate_org_unit(unit.to_pydantic())  # type: ignore

    # Related Units
    # -------------

    # Roles
    # -----

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
