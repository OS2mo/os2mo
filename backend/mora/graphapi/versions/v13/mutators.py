# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Like latest, but with schema models from this version, with old resolvers."""
import logging
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID

import strawberry
from pydantic import parse_obj_as
from strawberry.file_uploads import Upload
from strawberry.types import Info

from ..latest.address import create_address
from ..latest.address import terminate_address
from ..latest.address import update_address
from ..latest.association import create_association
from ..latest.association import terminate_association
from ..latest.association import update_association
from ..latest.classes import delete_class
from ..latest.employee import create_employee
from ..latest.employee import terminate_employee
from ..latest.employee import update_employee
from ..latest.engagements import create_engagement
from ..latest.engagements import terminate_engagement
from ..latest.engagements import update_engagement
from ..latest.facets import delete_facet
from ..latest.inputs import AddressCreateInput
from ..latest.inputs import AddressTerminateInput
from ..latest.inputs import AddressUpdateInput
from ..latest.inputs import AssociationCreateInput
from ..latest.inputs import AssociationTerminateInput
from ..latest.inputs import AssociationUpdateInput
from ..latest.inputs import EmployeeCreateInput
from ..latest.inputs import EmployeeTerminateInput
from ..latest.inputs import EmployeeUpdateInput
from ..latest.inputs import EngagementCreateInput
from ..latest.inputs import EngagementTerminateInput
from ..latest.inputs import EngagementUpdateInput
from ..latest.inputs import ITAssociationCreateInput
from ..latest.inputs import ITAssociationTerminateInput
from ..latest.inputs import ITAssociationUpdateInput
from ..latest.inputs import ITUserCreateInput
from ..latest.inputs import ITUserTerminateInput
from ..latest.inputs import ITUserUpdateInput
from ..latest.inputs import KLECreateInput
from ..latest.inputs import KLETerminateInput
from ..latest.inputs import KLEUpdateInput
from ..latest.inputs import LeaveCreateInput
from ..latest.inputs import LeaveTerminateInput
from ..latest.inputs import LeaveUpdateInput
from ..latest.inputs import ManagerCreateInput
from ..latest.inputs import ManagerTerminateInput
from ..latest.inputs import ManagerUpdateInput
from ..latest.inputs import OrganisationUnitCreateInput
from ..latest.inputs import OrganisationUnitTerminateInput
from ..latest.inputs import OrganisationUnitUpdateInput
from ..latest.inputs import RelatedUnitsUpdateInput
from ..latest.inputs import RoleCreateInput
from ..latest.inputs import RoleTerminateInput
from ..latest.inputs import RoleUpdateInput
from ..latest.it_association import create_itassociation
from ..latest.it_association import terminate_itassociation
from ..latest.it_association import update_itassociation
from ..latest.it_user import create_ituser
from ..latest.it_user import terminate_ituser
from ..latest.it_user import update_ituser
from ..latest.itsystem import create_itsystem
from ..latest.itsystem import delete_itsystem
from ..latest.itsystem import update_itsystem
from ..latest.kle import create_kle
from ..latest.kle import terminate_kle
from ..latest.kle import update_kle
from ..latest.leave import create_leave
from ..latest.leave import terminate_leave
from ..latest.leave import update_leave
from ..latest.manager import create_manager
from ..latest.manager import terminate_manager
from ..latest.manager import update_manager
from ..latest.models import FileStore
from ..latest.models import ITSystemCreate as LatestITSystemCreate
from ..latest.models import ITSystemUpdate as LatestITSystemUpdate
from ..latest.org import create_org
from ..latest.org import OrganisationCreate
from ..latest.org_unit import create_org_unit
from ..latest.org_unit import terminate_org_unit
from ..latest.org_unit import update_org_unit
from ..latest.permissions import gen_create_permission
from ..latest.permissions import gen_delete_permission
from ..latest.permissions import gen_role_permission
from ..latest.permissions import gen_terminate_permission
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.related_units import update_related_units
from ..latest.role import create_role
from ..latest.role import terminate_role
from ..latest.role import update_role
from ..v14.version import GraphQLVersion as NextGraphQLVersion
from ..v14.version import ITSystemCreateInput
from ..v15.version import FacetCreateInput
from ..v15.version import FacetUpdateInput
from ..v16.version import ClassCreateInput
from ..v16.version import ClassUpdateInput
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
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from mora import db
from mora.auth.middleware import get_authenticated_user
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
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import RoleRead

logger = logging.getLogger(__name__)


def ensure_uuid(uuid: UUID | str) -> UUID:
    if isinstance(uuid, UUID):
        return uuid
    return UUID(uuid)


def uuid2response(uuid: UUID | str, model: Any) -> Response:
    return Response[model](uuid=ensure_uuid(uuid))


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
        return uuid2response(await terminate_address(input.to_pydantic()), AddressRead)

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
        return await NextGraphQLVersion.schema.mutation.class_create(
            self=self, info=info, input=input
        )

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
        return await NextGraphQLVersion.schema.mutation.class_update(
            self=self, info=info, input=input
        )

    # TODO: class_terminate

    @strawberry.mutation(
        description="Deletes a class." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("class"),
        ],
    )
    async def class_delete(self, uuid: UUID) -> Response[Class]:
        uuid = await delete_class(uuid)
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
        return await NextGraphQLVersion.schema.mutation.facet_create(
            self=self, info=info, input=input
        )

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
        return await NextGraphQLVersion.schema.mutation.facet_update(
            self=self, info=info, input=input
        )

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
        uuid = await delete_facet(uuid)
        return uuid2response(uuid, FacetRead)

    # ITAssociations
    # ---------
    @strawberry.mutation(
        description="Creates an IT-Association.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("association"),
        ],
    )
    async def itassociation_create(
        self, input: ITAssociationCreateInput
    ) -> Response[Association]:
        return uuid2response(
            await create_itassociation(input.to_pydantic()), AssociationRead
        )

    @strawberry.mutation(
        description="Updates an IT-Association.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("association"),
        ],
    )
    async def itassociation_update(
        self, input: ITAssociationUpdateInput
    ) -> Response[Association]:
        return uuid2response(
            await update_itassociation(input.to_pydantic()), AssociationRead
        )

    @strawberry.mutation(
        description="Terminates an ITAssociation.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("association"),
        ],
    )
    async def itassociation_terminate(
        self, input: ITAssociationTerminateInput
    ) -> Response[Association]:
        return uuid2response(
            await terminate_itassociation(input.to_pydantic()), AssociationRead
        )

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
        org = await info.context["org_loader"].load(0)
        v13_model = input.to_pydantic()
        latest_model = parse_obj_as(LatestITSystemCreate, v13_model.to_latest_dict())
        uuid = await create_itsystem(latest_model, org.uuid)
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
        org = await info.context["org_loader"].load(0)
        v13_model = input.to_pydantic()
        latest_model = parse_obj_as(LatestITSystemUpdate, v13_model.to_latest_dict())
        uuid = await update_itsystem(latest_model, org.uuid)  # type: ignore
        return uuid2response(uuid, ITSystemRead)

    @strawberry.mutation(
        description="Deletes an ITSystem." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("itsystem"),
        ],
    )
    async def itsystem_delete(self, uuid: UUID) -> Response[ITSystem]:
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

    @strawberry.mutation(
        description="Updates a leave.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("leave"),
        ],
    )
    async def leave_update(self, input: LeaveUpdateInput) -> Response[Leave]:
        return uuid2response(await update_leave(input.to_pydantic()), LeaveRead)

    @strawberry.mutation(
        description="Terminates a leave.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("leave"),
        ],
    )
    async def leave_terminate(self, input: LeaveTerminateInput) -> Response[Leave]:
        return uuid2response(await terminate_leave(input.to_pydantic()), LeaveRead)

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
        description="Creates an organisation unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("org_unit"),
        ],
    )
    async def org_unit_create(
        self, input: OrganisationUnitCreateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(await create_org_unit(input), OrganisationUnitRead)

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
        return uuid2response(await update_org_unit(input), OrganisationUnitRead)

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

    @strawberry.mutation(
        description="Updates relations for an org_unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("related_unit"),
        ],
    )
    async def related_units_update(
        self, input: RelatedUnitsUpdateInput
    ) -> Response[RelatedUnit]:
        return uuid2response(
            await update_related_units(input.to_pydantic()), RelatedUnitRead
        )

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

    @strawberry.mutation(
        description="Updates a role.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("role"),
        ],
    )
    async def role_update(self, input: RoleUpdateInput) -> Response[Role]:
        return uuid2response(await update_role(input.to_pydantic()), RoleRead)

    @strawberry.mutation(
        description="Terminates a role.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("role"),
        ],
    )
    async def role_terminate(self, input: RoleTerminateInput) -> Response[Role]:
        return uuid2response(await terminate_role(input.to_pydantic()), RoleRead)

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
        file_name = file.filename
        file_bytes = await file.read()

        actor = get_authenticated_user()

        await db.files.write(
            info.context["session"], actor, file_store, file_name, file_bytes, force
        )

        return "OK"


async def delete_organisationfunktion(uuid: UUID) -> UUID:
    """Delete an organisationfunktion by creating a "Slettet" (deleted) registration."""
    c = get_connector()
    uuid = await c.organisationfunktion.delete(uuid)
    return uuid
