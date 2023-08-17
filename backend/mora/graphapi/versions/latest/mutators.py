# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import logging
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload
from strawberry.types import Info

from .address import create_address
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
from .employee import create_employee
from .employee import terminate as terminate_employee
from .employee import update_employee
from .engagements import create_engagement
from .engagements import terminate_engagement
from .engagements import update_engagement
from .facets import create_facet
from .facets import delete_facet
from .facets import FacetCreateInput
from .facets import FacetUpdateInput
from .facets import update_facet
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
from .inputs import KLECreateInput
from .inputs import KLETerminateInput
from .inputs import KLEUpdateInput
from .inputs import LeaveCreateInput
from .inputs import ManagerCreateInput
from .inputs import ManagerTerminateInput
from .inputs import ManagerUpdateInput
from .inputs import OrganisationUnitCreateInput
from .inputs import OrganisationUnitTerminateInput
from .inputs import OrganisationUnitUpdateInput
from .inputs import RoleCreateInput
from .it_user import create as create_ituser
from .it_user import terminate as terminate_ituser
from .it_user import update as update_ituser
from .itsystem import create_itsystem
from .itsystem import delete_itsystem
from .itsystem import ITSystemCreateInput
from .itsystem import update_itsystem
from .kle import create_kle
from .kle import terminate_kle
from .kle import update_kle
from .leave import create_leave
from .manager import create_manager
from .manager import terminate_manager
from .manager import update_manager
from .models import FileStore
from .models import OrganisationUnitRefreshRead
from .org import create_org
from .org import OrganisationCreate
from .org_unit import create_org_unit
from .org_unit import terminate_org_unit
from .org_unit import trigger_org_unit_refresh
from .org_unit import update_org_unit
from .permissions import gen_create_permission
from .permissions import gen_delete_permission
from .permissions import gen_refresh_permission
from .permissions import gen_role_permission
from .permissions import gen_terminate_permission
from .permissions import gen_update_permission
from .permissions import IsAuthenticatedPermission
from .role import create_role
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Employee
from .schema import Engagement
from .schema import Facet
from .schema import ITSystem
from .schema import ITUser
from .schema import KLE
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import OrganisationUnitRefresh
from .schema import Response
from .schema import Role
from mora.common import get_connector
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITSystemRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import RoleRead

logger = logging.getLogger(__name__)


def ensure_uuid(uuid: UUID | str) -> UUID:
    if isinstance(uuid, UUID):
        return uuid
    return UUID(uuid)


def uuid2response(uuid: UUID | str, model: type) -> Response:
    return Response(uuid=ensure_uuid(uuid), model=model)  # type: ignore[call-arg]


delete_warning = dedent(
    """\

    **Warning**:
    This mutator does bitemporal deletion, **not** temporal termination.
    Do **not** use this mutator **unless** you **fully understand** its implications.

    Bitemporal deletion and temporal termination are **very** different operations and should **not** be confused.
    If you do not know which of the operations you need, you most likely need temporal termination.

    Bitemporal deletion works on the bitemporal time-axis, and should **only** be used by clients that **fully understand** the underlying bitemporal model, including how a bitemporal delete affects the registration history.

    After this call the deleted entity will no longer show up in **any** temporal listing.

    Note:
    It is currently the callers responsibility to ensure that references are dealt with before doing bitemporal deletions.
    Failure to do so **will** leave dangling references breaking temporal foreign-keys, and potentially breaking invariants in the data.
    """
)


@strawberry.type(
    description=dedent(
        """\
    Entrypoint for all modification-operations.

    **Warning**:
    Do **not** use any `*_delete`-mutators without **thoroughly** understanding its implications and the documentation.
    """
    )
)
class Mutation:
    # Addresses
    # ---------
    @strawberry.mutation(
        description="Creates an address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("address"),
        ],
    )
    async def address_create(self, input: AddressCreateInput) -> Response[Address]:
        return uuid2response(await create_address(input.to_pydantic()), AddressRead)  # type: ignore

    @strawberry.mutation(
        description="Updates an address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("address"),
        ],
    )
    async def address_update(self, input: AddressUpdateInput) -> Response[Address]:
        return uuid2response(await update_address(input.to_pydantic()), AddressRead)  # type: ignore

    @strawberry.mutation(
        description="Terminates an address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("address"),
        ],
    )
    async def address_terminate(
        self, input: AddressTerminateInput
    ) -> Response[Address]:
        return uuid2response(await terminate_addr(input.to_pydantic()), AddressRead)

    @strawberry.mutation(
        description="Deletes an address." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("address"),
        ],
    )
    async def address_delete(self, uuid: UUID) -> Response[Address]:
        return uuid2response(await delete_organisationfunktion(uuid), AddressRead)

    # Associations
    # ------------
    @strawberry.mutation(
        description="Creates an association.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("association"),
        ],
    )
    async def association_create(
        self, input: AssociationCreateInput
    ) -> Response[Association]:
        return uuid2response(
            await create_association(input.to_pydantic()), AssociationRead  # type: ignore
        )

    @strawberry.mutation(
        description="Updates an association.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("association"),
        ],
    )
    async def association_update(
        self, input: AssociationUpdateInput
    ) -> Response[Association]:
        return uuid2response(
            await update_association(input.to_pydantic()), AssociationRead  # type: ignore
        )

    @strawberry.mutation(
        description="Terminates an association",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("association"),
        ],
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
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("class"),
        ],
    )
    async def class_create(
        self, info: Info, input: ClassCreateInput
    ) -> Response[Class]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_class(input.to_pydantic(), org.uuid, note)
        return uuid2response(uuid, ClassRead)

    @strawberry.mutation(
        description="Updates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("class"),
        ],
    )
    async def class_update(
        self, info: Info, input: ClassUpdateInput
    ) -> Response[Class]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await update_class(input.to_pydantic(), input.uuid, org.uuid, note)  # type: ignore
        return uuid2response(uuid, ClassRead)

    # TODO: class_terminate

    @strawberry.mutation(
        description="Deletes a class." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("class"),
        ],
    )
    async def class_delete(self, uuid: UUID) -> Response[Class]:
        note = ""
        uuid = await delete_class(uuid, note)
        return uuid2response(uuid, ClassRead)

    # Employees
    # ---------
    # Rename all 'employee' mutators and objects to 'person'
    @strawberry.mutation(
        description="Creates an employee.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("employee"),
        ],
    )
    async def employee_create(self, input: EmployeeCreateInput) -> Response[Employee]:
        return uuid2response(await create_employee(input.to_pydantic()), EmployeeRead)  # type: ignore

    @strawberry.mutation(
        description="Updates an employee.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("employee"),
        ],
    )
    async def employee_update(self, input: EmployeeUpdateInput) -> Response[Employee]:
        return uuid2response(await update_employee(input.to_pydantic()), EmployeeRead)  # type: ignore

    @strawberry.mutation(
        description="Terminates an employee.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("employee"),
        ],
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
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("engagement"),
        ],
    )
    async def engagement_create(
        self, input: EngagementCreateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await create_engagement(input.to_pydantic()), EngagementRead  # type: ignore
        )

    @strawberry.mutation(
        description="Updates an engagement.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("engagement"),
        ],
    )
    async def engagement_update(
        self, input: EngagementUpdateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await update_engagement(input.to_pydantic()), EngagementRead  # type: ignore
        )

    @strawberry.mutation(
        description="Terminates an engagement.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("engagement"),
        ],
    )
    async def engagement_terminate(
        self, input: EngagementTerminateInput
    ) -> Response[Engagement]:
        return uuid2response(
            await terminate_engagement(input.to_pydantic()), EngagementRead
        )

    @strawberry.mutation(
        description="Deletes an engagement." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("engagement"),
        ],
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
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("facet"),
        ],
    )
    async def facet_create(
        self, info: Info, input: FacetCreateInput
    ) -> Response[Facet]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_facet(input.to_pydantic(), org.uuid, note)
        return uuid2response(uuid, FacetRead)

    @strawberry.mutation(
        description="Updates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("facet"),
        ],
    )
    async def facet_update(
        self, info: Info, input: FacetUpdateInput
    ) -> Response[Facet]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await update_facet(input.to_pydantic(), input.uuid, org.uuid, note)  # type: ignore
        return uuid2response(uuid, FacetRead)

    # TODO: facet_update
    # TODO: facet_terminate

    @strawberry.mutation(
        description="Deletes a facet." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("facet"),
        ],
    )
    async def facet_delete(self, uuid: UUID) -> Response[Facet]:
        note = ""
        uuid = await delete_facet(uuid, note)
        return uuid2response(uuid, FacetRead)

    # ITSystems
    # ---------
    @strawberry.mutation(
        description="Creates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("itsystem"),
        ],
    )
    async def itsystem_create(
        self, info: Info, input: ITSystemCreateInput
    ) -> Response[ITSystem]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await create_itsystem(input.to_pydantic(), org.uuid, note)
        return uuid2response(uuid, ITSystemRead)

    @strawberry.mutation(
        description="Updates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("itsystem"),
        ],
    )
    async def itsystem_update(
        self, info: Info, input: ITSystemCreateInput
    ) -> Response[ITSystem]:
        note = ""
        org = await info.context["org_loader"].load(0)
        uuid = await update_itsystem(input.to_pydantic(), input.uuid, org.uuid, note)  # type: ignore
        return uuid2response(uuid, ITSystemRead)

    # TODO: itsystem_terminate

    @strawberry.mutation(
        description="Deletes an ITSystem." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("itsystem"),
        ],
    )
    async def itsystem_delete(self, info: Info, uuid: UUID) -> Response[ITSystem]:
        note = ""
        uuid = await delete_itsystem(uuid, note)
        return uuid2response(uuid, ITSystemRead)

    # ITUsers
    # -------
    @strawberry.mutation(
        description="Creates an IT-User.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("ituser"),
        ],
    )
    async def ituser_create(self, input: ITUserCreateInput) -> Response[ITUser]:
        return uuid2response(await create_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Updates an IT-User.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("ituser"),
        ],
    )
    async def ituser_update(self, input: ITUserUpdateInput) -> Response[ITUser]:
        return uuid2response(await update_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Terminates IT-User.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("ituser"),
        ],
    )
    async def ituser_terminate(self, input: ITUserTerminateInput) -> Response[ITUser]:
        return uuid2response(await terminate_ituser(input.to_pydantic()), ITUserRead)

    @strawberry.mutation(
        description="Deletes an IT-User." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("ituser"),
        ],
    )
    async def ituser_delete(self, uuid: UUID) -> Response[ITUser]:
        return uuid2response(await delete_organisationfunktion(uuid), ITUserRead)

    # KLEs
    # ----
    @strawberry.mutation(
        description="Creates a KLE annotation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("kle"),
        ],
    )
    async def kle_create(self, input: KLECreateInput) -> Response[KLE]:
        return uuid2response(await create_kle(input.to_pydantic()), KLERead)

    @strawberry.mutation(
        description="Updates a KLE annotation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("kle"),
        ],
    )
    async def kle_update(self, input: KLEUpdateInput) -> Response[KLE]:
        return uuid2response(await update_kle(input.to_pydantic()), KLERead)

    @strawberry.mutation(
        description="Terminates a KLE annotation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("kle"),
        ],
    )
    async def kle_terminate(self, input: KLETerminateInput) -> Response[KLE]:
        return uuid2response(await terminate_kle(input.to_pydantic()), KLERead)

    # TODO: kle_delete

    # Leave
    # -----
    @strawberry.mutation(
        description="Creates a leave.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("leave"),
        ],
    )
    async def leave_create(self, input: LeaveCreateInput) -> Response[Leave]:
        return uuid2response(await create_leave(input.to_pydantic()), LeaveRead)

    # TODO: leave_update
    # TODO: leave_terminate
    # TODO: leave_delete

    # Managers
    # --------
    @strawberry.mutation(
        description="Creates a manager relation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("manager"),
        ],
    )
    async def manager_create(self, input: ManagerCreateInput) -> Response[Manager]:
        return uuid2response(await create_manager(input.to_pydantic()), ManagerRead)

    @strawberry.mutation(
        description="Updates a manager relation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("manager"),
        ],
    )
    async def manager_update(self, input: ManagerUpdateInput) -> Response[Manager]:
        return uuid2response(await update_manager(input.to_pydantic()), ManagerRead)

    @strawberry.mutation(
        description="Terminates a manager relation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("manager"),
        ],
    )
    async def manager_terminate(
        self, input: ManagerTerminateInput
    ) -> Response[Manager]:
        return uuid2response(await terminate_manager(input.to_pydantic()), ManagerRead)

    # TODO: manager_delete

    # Root Organisation
    # -----------------
    @strawberry.mutation(
        description="Creates the root-organisation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("org"),
        ],
        deprecation_reason="The root organisation concept will be removed in a future version of OS2mo.",
    )
    async def org_create(self, info: Info, input: OrganisationCreate) -> Organisation:
        # Called for side-effect
        await create_org(input)
        return await info.context["org_loader"].load(0)

    # TODO: org_update
    # TODO: org_terminate
    # TODO: org_delete

    # Organisational Units
    # --------------------
    @strawberry.mutation(
        description="Trigger refresh for an organisation unit",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("org_unit"),
        ],
        deprecation_reason="The mutator will be removed in a future version of OS2mo",
    )
    async def org_unit_refresh(self, uuid: UUID) -> OrganisationUnitRefresh:
        result = await trigger_org_unit_refresh(uuid)
        organisation_unit_refresh = OrganisationUnitRefreshRead(**result)
        return OrganisationUnitRefresh.from_pydantic(organisation_unit_refresh)

    @strawberry.mutation(
        description="Creates an organisation unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("org_unit"),
        ],
    )
    async def org_unit_create(
        self, input: OrganisationUnitCreateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await create_org_unit(input.to_pydantic()), OrganisationUnitRead
        )

    @strawberry.mutation(
        description="Updates an organisation unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("org_unit"),
        ],
    )
    async def org_unit_update(
        self, input: OrganisationUnitUpdateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await update_org_unit(input.to_pydantic()), OrganisationUnitRead
        )

    @strawberry.mutation(
        description="Terminates an organization unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("org_unit"),
        ],
    )
    async def org_unit_terminate(
        self, input: OrganisationUnitTerminateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await terminate_org_unit(input.to_pydantic()), OrganisationUnitRead
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

    @strawberry.mutation(
        description="Creates a role.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("role"),
        ],
    )
    async def role_create(self, input: RoleCreateInput) -> Response[Role]:
        return uuid2response(await create_role(input.to_pydantic()), RoleRead)

    # TODO: roles_update
    # TODO: roles_terminate
    # TODO: roles_delete

    # Files
    # -----
    @strawberry.mutation(
        description=dedent(
            """\
            Upload a file.

            File upload must be done via multipart form-data.

            How to do this is client-specific, but below is an example using [curl](https://curl.se/):
            ```console
            curl https://{{MO_URL}}/graphql/v7 \\
              -H "Authorization: Bearer {{TOKEN}}" \\
              -F operations="{\\\"query\\\": \\\"{{QUERY}}\\\", \\
                  \\\"variables\\\": {\\\"file\\\": null}}" \\
              -F map='{"file": ["variables.file"]}' \\
              -F file=@myfile.txt
            ```
            Where:
            * `myfile.txt` is the file to upload.
            * `{{MO_URL}}` is the base-url for the OS2mo instance to upload the file to.
            * `{{TOKEN}}` is a valid JWT-token acquired from Keycloak.
            * `{{QUERY}}` is the upload query:
            ```gql
            mutation($file: Upload!) {
              upload_file(
                file_store: EXPORTS,
                file: $file
              )
            }
            ```

            Note:
            As GraphiQL does not support sending multipart form-data payloads, it is unfortunately not possible to upload files from GraphiQL.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("upload_files"),
        ],
    )
    async def upload_file(
        self,
        info: Info,
        file_store: Annotated[
            FileStore,
            strawberry.argument(description="The filestore to upload the file into"),
        ],
        file: Annotated[
            Upload,
            strawberry.argument(
                description=dedent(
                    """\
                    Multipart form-data file payload.

                    Contains both the data and the filename to be uploaded.

                    See the `upload_file`-mutator description for how to send this.
                    """
                )
            ),
        ],
        force: Annotated[
            bool,
            strawberry.argument(description="Whether to override pre-existing files."),
        ] = False,
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
