# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
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
from .classes import ClassCreateInput
from .classes import ClassUpdateInput
from .classes import create_class
from .classes import delete_class
from .classes import update_class
from .employee import create as employee_create
from .employee import terminate as terminate_employee
from .employee import update as employee_update
from .engagements import create_engagement
from .engagements import terminate_engagement
from .engagements import update_engagement
from .facets import create_facet
from .facets import delete_facet
from .facets import FacetCreateInput
from .inputs import AddressCreateInput
from .inputs import AddressTerminateInput
from .inputs import AddressUpdateInput
from .inputs import AssociationCreateInput
from .inputs import AssociationTerminateInput
from .inputs import AssociationUpdateInput
from .inputs import EmployeeCreateInput
from .inputs import EmployeeTerminateInput
from .inputs import EmployeeUpdateInput
from .inputs import EngagementCreateInput
from .inputs import EngagementTerminateInput
from .inputs import EngagementUpdateInput
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
from .itsystem import create_itsystem
from .itsystem import delete_itsystem
from .itsystem import ITSystemCreateInput
from .itsystem import update_itsystem
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
from .permissions import IsAuthenticatedPermission
from .schema import Address
from .schema import Association
from .schema import Employee
from .schema import Engagement
from .schema import ITUser
from .schema import Manager
from .schema import OrganisationUnit
from .schema import OrganisationUnitRefresh
from .schema import Response
from .types import UUIDReturn
from mora.common import get_connector
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import ManagerRead

logger = logging.getLogger(__name__)

# NOTE: The end goal is not to require admin for all GraphQL mutators, but rather to
# have unique roles for each mutator.
# The current solution is merely to stop unauthorized access to writing.
# TODO: Implement proper permissions
admin_permission_class = gen_role_permission("admin", force_permission_check=True)


def ensure_uuid(uuid: UUID | str) -> UUID:
    if isinstance(uuid, UUID):
        return uuid
    return UUID(uuid)


def uuid2response(uuid: UUID | str, model: type) -> Response:
    return Response(uuid=ensure_uuid(uuid), model=model)


@strawberry.type
class Mutation:
    # Addresses
    # ---------
    @strawberry.mutation(
        description="Creates an address.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def address_create(self, input: AddressCreateInput) -> Response[Address]:
        return uuid2response(await create_address(input.to_pydantic()), AddressRead)

    @strawberry.mutation(
        description="Updates an address.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def address_update(self, input: AddressUpdateInput) -> Response[Address]:
        return uuid2response(await update_address(input.to_pydantic()), AddressRead)

    @strawberry.mutation(
        description="Terminates an address.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def address_terminate(self, at: AddressTerminateInput) -> Response[Address]:
        return uuid2response(await terminate_addr(at.to_pydantic()), AddressRead)

    @strawberry.mutation(
        description="Deletes an address.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def address_delete(self, uuid: UUID) -> Response[Address]:
        return uuid2response(await delete_organisationfunktion(uuid), AddressRead)

    # Associations
    # ------------
    @strawberry.mutation(
        description="Creates an association.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def association_create(
        self, input: AssociationCreateInput
    ) -> Response[Association]:
        return uuid2response(
            await create_association(input.to_pydantic()), AssociationRead
        )

    @strawberry.mutation(
        description="Updates an association.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def association_update(
        self, input: AssociationUpdateInput
    ) -> Response[Association]:
        return uuid2response(
            await update_association(input.to_pydantic()), AssociationRead
        )

    @strawberry.mutation(
        description="Terminates an association",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def association_terminate(
        self, input: AssociationTerminateInput
    ) -> Response[Association]:
        return uuid2response(
            await terminate_association(input.to_pydantic()), AssociationRead
        )

    # TODO: association_delete

    # Classes
    # -------
    @strawberry.mutation(
        description="Creates a class.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def class_create(self, info: Info, input: ClassCreateInput) -> UUIDReturn:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_class(input.to_pydantic(), org.uuid, note)
        return UUIDReturn(uuid=uuid)

    @strawberry.mutation(
        description="Updates a class.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def class_update(
        self, info: Info, uuid: UUID, input: ClassUpdateInput
    ) -> UUIDReturn:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await update_class(input.to_pydantic(), uuid, org.uuid, note)
        return UUIDReturn(uuid=uuid)

    # TODO: class_terminate

    @strawberry.mutation(
        description="Deletes a class.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def class_delete(self, uuid: UUID) -> UUIDReturn:
        note = ""
        uuid = await delete_class(uuid, note)
        return UUIDReturn(uuid=uuid)

    # Employees
    # ---------
    @strawberry.mutation(
        description="Creates an employee.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def employee_create(self, input: EmployeeCreateInput) -> Response[Employee]:
        return uuid2response(await employee_create(input.to_pydantic()), EmployeeRead)

    @strawberry.mutation(
        description="Updates an employee.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def employee_update(self, input: EmployeeUpdateInput) -> Response[Employee]:
        return uuid2response(await employee_update(input.to_pydantic()), EmployeeRead)

    @strawberry.mutation(
        description="Terminates an employee.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def employee_terminate(
        self, input: EmployeeTerminateInput
    ) -> Response[Employee]:
        return uuid2response(
            await terminate_employee(input.to_pydantic()), EmployeeRead
        )

    # TODO: employee_delete

    # Engagements
    # -----------
    @strawberry.mutation(
        description="Creates an engagement.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def engagement_create(
        self, input: EngagementCreateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await create_engagement(input.to_pydantic()), EngagementRead
        )

    @strawberry.mutation(
        description="Updates an engagement.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def engagement_update(
        self, input: EngagementUpdateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await update_engagement(input.to_pydantic()), EngagementRead
        )

    @strawberry.mutation(
        description="Terminates an engagement.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def engagement_terminate(
        self, input: EngagementTerminateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await terminate_engagement(input.to_pydantic()), EngagementRead
        )

    @strawberry.mutation(
        description="Deletes an engagement.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def engagement_delete(self, uuid: UUID) -> Response[Engagement]:
        return uuid2response(await delete_organisationfunktion(uuid), EngagementRead)

    # EngagementsAssociations
    # -----------------------

    # TODO: engagement_association_create
    # TODO: engagement_association_update
    # TODO: engagement_association_terminate
    # TODO: engagement_association_delete

    # Facets
    # ------
    @strawberry.mutation(
        description="Creates a facet.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def facet_create(self, info: Info, input: FacetCreateInput) -> UUIDReturn:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_facet(input.to_pydantic(), org.uuid, note)
        return UUIDReturn(uuid=uuid)

    # TODO: facet_update
    # TODO: facet_terminate

    @strawberry.mutation(
        description="Deletes a facet.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def facet_delete(self, uuid: UUID) -> UUIDReturn:
        note = ""
        uuid = await delete_facet(uuid, note)
        return UUIDReturn(uuid=uuid)

    # ITSystems
    # ---------
    @strawberry.mutation(
        description="Creates an ITSystem.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def itsystem_create(
        self, info: Info, input: ITSystemCreateInput
    ) -> UUIDReturn:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_itsystem(input.to_pydantic(), org.uuid, note)
        return UUIDReturn(uuid=uuid)

    @strawberry.mutation(
        description="Updates an ITSystem.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def itsystem_update(
        self, info: Info, input: ITSystemCreateInput, uuid: UUID
    ) -> UUIDReturn:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await update_itsystem(input.to_pydantic(), uuid, org.uuid, note)
        return UUIDReturn(uuid=uuid)

    # TODO: itsystem_terminate

    @strawberry.mutation(
        description="Deletes an ITSystem.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def itsystem_delete(self, info: Info, uuid: UUID) -> UUIDReturn:
        note = ""
        uuid = await delete_itsystem(uuid, note)
        return UUIDReturn(uuid=uuid)

    # ITUsers
    # -------
    @strawberry.mutation(
        description="Creates an IT-User.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def ituser_create(self, input: ITUserCreateInput) -> Response[ITUser]:
        return uuid2response(await create_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Updates an IT-User.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def ituser_update(self, input: ITUserUpdateInput) -> Response[ITUser]:
        return uuid2response(await update_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Terminates IT-User.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def ituser_terminate(self, input: ITUserTerminateInput) -> Response[ITUser]:
        return uuid2response(await terminate_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Deletes an IT-User.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def ituser_delete(self, uuid: UUID) -> Response[ITUser]:
        return uuid2response(await delete_organisationfunktion(uuid), ITUserRead)

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
        description="Creates a manager relation.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def manager_create(self, input: ManagerCreateInput) -> Response[Manager]:
        return uuid2response(await create_manager(input.to_pydantic()), ManagerRead)

    @strawberry.mutation(
        description="Updates a manager relation.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def manager_update(self, input: ManagerUpdateInput) -> Response[Manager]:
        return uuid2response(await update_manager(input.to_pydantic()), ManagerRead)

    @strawberry.mutation(
        description="Terminates a manager relation.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def manager_terminate(
        self, input: ManagerTerminateInput
    ) -> Response[Manager]:
        return uuid2response(await terminate_manager(input.to_pydantic()), ManagerRead)

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
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def org_unit_refresh(self, uuid: UUID) -> OrganisationUnitRefresh:
        result = await trigger_org_unit_refresh(uuid)
        organisation_unit_refresh = OrganisationUnitRefreshRead(**result)
        return OrganisationUnitRefresh.from_pydantic(organisation_unit_refresh)

    @strawberry.mutation(
        description="Creates an organisation unit.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def org_unit_create(
        self, input: OrganisationUnitCreateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await create_org_unit(input.to_pydantic()), OrganisationUnitRead
        )

    @strawberry.mutation(
        description="Updates an organisation unit.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def org_unit_update(
        self, input: OrganisationUnitUpdateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await update_org_unit(input.to_pydantic()), OrganisationUnitRead
        )

    @strawberry.mutation(
        description="Terminates an organization unit.",
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def org_unit_terminate(
        self, unit: OrganisationUnitTerminateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await terminate_org_unit(unit.to_pydantic()), OrganisationUnitRead
        )

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
        permission_classes=[IsAuthenticatedPermission, admin_permission_class],
    )
    async def upload_file(
        self, info: Info, file_store: FileStore, file: Upload, force: bool = False
    ) -> str:
        filestorage = info.context["filestorage"]

        file_name = file.filename
        file_bytes = await file.read()
        filestorage.save_file(file_store, file_name, file_bytes, force)
        return "OK"


async def delete_organisationfunktion(uuid: UUID) -> UUID:
    """Delete an organisationfunktion by creating a "Slettet" (deleted) registration."""
    c = get_connector()
    uuid = await c.organisationfunktion.delete(uuid)
    return uuid
