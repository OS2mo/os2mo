# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import logging
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID

import sqlalchemy
import strawberry
from fastramqpi.ra_utils.asyncio_utils import gather_with_concurrency
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from strawberry.file_uploads import Upload
from strawberry.types import Info

from mora import db
from mora.auth.middleware import get_authenticated_user
from mora.common import get_connector
from mora.db import AsyncSession
from mora.db.events import METRIC_ACKNOWLEDGED_EVENTS
from mora.db.events import add_event
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import OwnerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead

from ...custom_schema import get_version
from ...fields import Metadata
from ...version import Version
from .address import create_address
from .address import terminate_address
from .address import update_address
from .association import create_association
from .association import terminate_association
from .association import update_association
from .classes import create_class
from .classes import delete_class
from .classes import terminate_class
from .classes import update_class
from .employee import create_employee
from .employee import terminate_employee
from .employee import update_employee
from .engagements import create_engagement
from .engagements import terminate_engagement
from .engagements import update_engagement
from .events import Listener
from .events import Namespace
from .facets import create_facet
from .facets import delete_facet
from .facets import terminate_facet
from .facets import update_facet
from .filters import AddressFilter
from .filters import AssociationFilter
from .filters import ClassFilter
from .filters import EmployeeFilter
from .filters import EngagementFilter
from .filters import FacetFilter
from .filters import ITSystemFilter
from .filters import ITUserFilter
from .filters import KLEFilter
from .filters import LeaveFilter
from .filters import ManagerFilter
from .filters import OrganisationUnitFilter
from .filters import OwnerFilter
from .filters import RelatedUnitFilter
from .filters import RoleBindingFilter
from .inputs import AddressCreateInput
from .inputs import AddressTerminateInput
from .inputs import AddressUpdateInput
from .inputs import AssociationCreateInput
from .inputs import AssociationTerminateInput
from .inputs import AssociationUpdateInput
from .inputs import ClassCreateInput
from .inputs import ClassTerminateInput
from .inputs import ClassTerminateInputV18
from .inputs import ClassUpdateInput
from .inputs import EmployeeCreateInput
from .inputs import EmployeeTerminateInput
from .inputs import EmployeeUpdateInput
from .inputs import EngagementCreateInput
from .inputs import EngagementTerminateInput
from .inputs import EngagementUpdateInput
from .inputs import EventAcknowledgeInput
from .inputs import EventSendInput
from .inputs import EventSilenceInput
from .inputs import EventUnsilenceInput
from .inputs import FacetCreateInput
from .inputs import FacetTerminateInput
from .inputs import FacetTerminateInputV18
from .inputs import FacetUpdateInput
from .inputs import ITAssociationCreateInput
from .inputs import ITAssociationTerminateInput
from .inputs import ITAssociationUpdateInput
from .inputs import ITSystemCreateInput
from .inputs import ITSystemTerminateInput
from .inputs import ITSystemTerminateInputV18
from .inputs import ITSystemUpdateInput
from .inputs import ITUserCreateInput
from .inputs import ITUserTerminateInput
from .inputs import ITUserUpdateInput
from .inputs import KLECreateInput
from .inputs import KLETerminateInput
from .inputs import KLEUpdateInput
from .inputs import LeaveCreateInput
from .inputs import LeaveTerminateInput
from .inputs import LeaveUpdateInput
from .inputs import ListenerCreateInput
from .inputs import ListenerDeleteInput
from .inputs import ManagerCreateInput
from .inputs import ManagerTerminateInput
from .inputs import ManagerUpdateInput
from .inputs import NamespaceCreateInput
from .inputs import NamespaceDeleteInput
from .inputs import OrganisationUnitCreateInput
from .inputs import OrganisationUnitTerminateInput
from .inputs import OrganisationUnitUpdateInput
from .inputs import OwnerCreateInput
from .inputs import OwnerTerminateInput
from .inputs import OwnerUpdateInput
from .inputs import RelatedUnitsUpdateInput
from .inputs import RoleBindingCreateInput
from .inputs import RoleBindingTerminateInput
from .inputs import RoleBindingUpdateInput
from .it_association import create_itassociation
from .it_association import terminate_itassociation
from .it_association import update_itassociation
from .it_user import create_ituser
from .it_user import terminate_ituser
from .it_user import update_ituser
from .itsystem import create_itsystem
from .itsystem import delete_itsystem
from .itsystem import terminate_itsystem
from .itsystem import update_itsystem
from .kle import create_kle
from .kle import terminate_kle
from .kle import update_kle
from .leave import create_leave
from .leave import terminate_leave
from .leave import update_leave
from .manager import create_manager
from .manager import terminate_manager
from .manager import update_manager
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import FileStore
from .models import RoleBindingRead
from .org import OrganisationCreate
from .org import create_org
from .org_unit import create_org_unit
from .org_unit import terminate_org_unit
from .org_unit import update_org_unit
from .owner import create_owner
from .owner import terminate_owner
from .owner import update_owner
from .paged import CursorType
from .paged import LimitType
from .paged import Paged
from .permissions import IsAuthenticatedPermission
from .permissions import gen_create_permission
from .permissions import gen_delete_permission
from .permissions import gen_refresh_permission
from .permissions import gen_role_permission
from .permissions import gen_terminate_permission
from .permissions import gen_update_permission
from .query import to_paged_uuids
from .related_units import update_related_units
from .resolvers import address_resolver
from .resolvers import association_resolver
from .resolvers import class_resolver
from .resolvers import employee_resolver
from .resolvers import engagement_resolver
from .resolvers import facet_resolver
from .resolvers import it_system_resolver
from .resolvers import it_user_resolver
from .resolvers import kle_resolver
from .resolvers import leave_resolver
from .resolvers import manager_resolver
from .resolvers import organisation_unit_resolver
from .resolvers import owner_resolver
from .resolvers import related_unit_resolver
from .resolvers import rolebinding_resolver
from .role import create_rolebinding
from .role import terminate_rolebinding
from .role import update_rolebinding
from .schema import KLE
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Employee
from .schema import Engagement
from .schema import Facet
from .schema import ITSystem
from .schema import ITUser
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import Owner
from .schema import RelatedUnit
from .schema import Response
from .schema import RoleBinding

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

QueueType = Annotated[
    str | None,
    strawberry.argument(
        deprecation_reason="Never worked properly. Use `exchange` to target a specific integration instead."
    ),
]


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
        description="Creates a list of address.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("address"),
        ],
    )
    async def addresses_create(
        self, input: list[AddressCreateInput]
    ) -> list[Response[Address]]:
        created_addresses = await asyncio.gather(
            *[Mutation.address_create(self, address) for address in input]
        )
        return created_addresses

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
        return uuid2response(await terminate_address(input.to_pydantic()), AddressRead)  # type: ignore

    @strawberry.mutation(
        description="Deletes an address." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("address"),
        ],
    )
    async def address_delete(self, uuid: UUID) -> Response[Address]:
        return uuid2response(await delete_organisationfunktion(uuid), AddressRead)

    @strawberry.mutation(
        description="Refresh addresses.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("address"),
        ],
    )
    async def address_refresh(
        self,
        info: Info,
        filter: AddressFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(address_resolver, Address)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="address", exchange=exchange, owner=owner
        )

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
            await create_association(input.to_pydantic()),  # type: ignore
            AssociationRead,
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
            await update_association(input.to_pydantic()),  # type: ignore
            AssociationRead,
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

    @strawberry.mutation(
        description="Refresh associations.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("association"),
        ],
    )
    async def association_refresh(
        self,
        info: Info,
        filter: AssociationFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(association_resolver, Association)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info,
            page=page,
            model="association",
            exchange=exchange,
            owner=owner,
        )

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
        org = await info.context["org_loader"].load(0)
        uuid = await create_class(input.to_pydantic(), org.uuid)
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
        org = await info.context["org_loader"].load(0)
        uuid = await update_class(input.to_pydantic(), org.uuid)
        # coverage: pause
        return uuid2response(uuid, ClassRead)
        # coverage: unpause

    @strawberry.mutation(
        name="class_terminate",
        description="Terminates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("class"),
        ],
        metadata=Metadata(version=lambda v: v <= Version.VERSION_18),
    )
    async def class_terminate__v18(
        self, input: ClassTerminateInputV18
    ) -> Response[Class]:
        return await Mutation.class_terminate(
            self,
            input=ClassTerminateInput(
                uuid=input.uuid,  # type: ignore[attr-defined]
                from_date=input.validity.from_date,  # type: ignore[attr-defined]
                to_date=input.validity.to_date,  # type: ignore[attr-defined]
            ),
        )

    @strawberry.mutation(
        description="Terminates a class.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("class"),
        ],
        metadata=Metadata(version=lambda v: v >= Version.VERSION_19),
    )
    async def class_terminate(self, input: ClassTerminateInput) -> Response[Class]:
        return uuid2response(await terminate_class(input.to_pydantic()), ClassRead)

    @strawberry.mutation(
        description="Deletes a class." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("class"),
        ],
    )
    async def class_delete(self, uuid: UUID) -> Response[Class]:
        uuid = await delete_class(uuid)
        # coverage: pause
        return uuid2response(uuid, ClassRead)
        # coverage: unpause

    @strawberry.mutation(
        description="Refresh classes.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("class"),
        ],
    )
    async def class_refresh(
        self,
        info: Info,
        filter: ClassFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(class_resolver, Class)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="class", exchange=exchange, owner=owner
        )

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

    @strawberry.mutation(
        description="Deletes an employee." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("employee"),
        ],
    )
    async def employee_delete(self, uuid: UUID) -> Response[Employee]:
        return uuid2response(await delete_bruger(uuid), EmployeeRead)

    @strawberry.mutation(
        description="Refresh employees.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("employee"),
        ],
    )
    async def employee_refresh(
        self,
        info: Info,
        filter: EmployeeFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(employee_resolver, Employee)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        # NOTE: "employee" is called "person" in the new AMQP system
        # coverage: pause
        return await refresh(
            info=info, page=page, model="person", exchange=exchange, owner=owner
        )
        # coverage: unpause

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
            await create_engagement(input.to_pydantic()),  # type: ignore
            EngagementRead,
        )

    @strawberry.mutation(
        description="Creates a list of engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("engagement"),
        ],
    )
    async def engagements_create(
        self, input: list[EngagementCreateInput]
    ) -> list[Response[Engagement]]:
        created_engagements = await asyncio.gather(
            *[Mutation.engagement_create(self, engagement) for engagement in input]
        )
        return created_engagements

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
            await update_engagement(input.to_pydantic()),  # type: ignore
            EngagementRead,
        )

    @strawberry.mutation(
        description=dedent(
            """\
            Updates a list of engagements.

            Note: If any of the updates in the transaction is a noop, the whole
            transaction will fail with the error:
            `(psycopg.errors.InFailedSqlTransaction) current transaction is aborted,
            commands ignored until end of transaction block`

            https://redmine.magenta.dk/issues/60573
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("engagement"),
        ],
    )
    async def engagements_update(
        self, input: list[EngagementUpdateInput]
    ) -> list[Response[Engagement]]:
        updated_engagements = await asyncio.gather(
            *[Mutation.engagement_update(self, engagement) for engagement in input]
        )
        return updated_engagements

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

    @strawberry.mutation(
        description="Refresh engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("engagement"),
        ],
    )
    async def engagement_refresh(
        self,
        info: Info,
        filter: EngagementFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(engagement_resolver, Engagement)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info,
            page=page,
            model="engagement",
            exchange=exchange,
            owner=owner,
        )

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
        org = await info.context["org_loader"].load(0)
        uuid = await create_facet(input.to_pydantic(), org.uuid)
        # coverage: pause
        return uuid2response(uuid, FacetRead)
        # coverage: unpause

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
        org = await info.context["org_loader"].load(0)
        uuid = await update_facet(input.to_pydantic(), org.uuid)
        # coverage: pause
        return uuid2response(uuid, FacetRead)
        # coverage: unpause

    @strawberry.mutation(
        name="facet_terminate",
        description="Terminates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("facet"),
        ],
        metadata=Metadata(version=lambda v: v <= Version.VERSION_18),
    )
    async def facet_terminate__v18(
        self, input: FacetTerminateInputV18
    ) -> Response[Facet]:
        return await Mutation.facet_terminate(
            self,
            input=FacetTerminateInput(
                uuid=input.uuid,  # type: ignore[attr-defined]
                from_date=input.validity.from_date,  # type: ignore[attr-defined]
                to_date=input.validity.to_date,  # type: ignore[attr-defined]
            ),
        )

    @strawberry.mutation(
        description="Terminates a facet.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("facet"),
        ],
        metadata=Metadata(version=lambda v: v >= Version.VERSION_19),
    )
    async def facet_terminate(self, input: FacetTerminateInput) -> Response[Facet]:
        return uuid2response(await terminate_facet(input.to_pydantic()), FacetRead)

    @strawberry.mutation(
        description="Deletes a facet." + delete_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("facet"),
        ],
    )
    async def facet_delete(self, uuid: UUID) -> Response[Facet]:
        uuid = await delete_facet(uuid)
        # coverage: pause
        return uuid2response(uuid, FacetRead)
        # coverage: unpause

    @strawberry.mutation(
        description="Refresh facets.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("facet"),
        ],
    )
    async def facet_refresh(
        self,
        info: Info,
        filter: FacetFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(facet_resolver, Facet)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="facet", exchange=exchange, owner=owner
        )

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
        uuid = await create_itsystem(input.to_pydantic(), org.uuid)
        # coverage: pause
        return uuid2response(uuid, ITSystemRead)
        # coverage: unpause

    @strawberry.mutation(
        description="Updates an ITSystem.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("itsystem"),
        ],
    )
    async def itsystem_update(
        self, info: Info, input: ITSystemUpdateInput
    ) -> Response[ITSystem]:
        org = await info.context["org_loader"].load(0)
        uuid = await update_itsystem(input.to_pydantic(), org.uuid)  # type: ignore
        # coverage: pause
        return uuid2response(uuid, ITSystemRead)
        # coverage: unpause

    @strawberry.mutation(
        name="itsystem_terminate",
        description="Terminates an IT-System.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("itsystem"),
        ],
        metadata=Metadata(version=lambda v: v <= Version.VERSION_18),
    )
    async def itsystem_terminate__v18(
        self, input: ITSystemTerminateInputV18
    ) -> Response[ITSystem]:
        return await Mutation.itsystem_terminate(
            self,
            input=ITSystemTerminateInput(
                uuid=input.uuid,  # type: ignore[attr-defined]
                from_date=input.validity.from_date,  # type: ignore[attr-defined]
                to_date=input.validity.to_date,  # type: ignore[attr-defined]
            ),
        )

    @strawberry.mutation(
        description="Terminates an IT-System.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_terminate_permission("itsystem"),
        ],
        metadata=Metadata(version=lambda v: v >= Version.VERSION_19),
    )
    async def itsystem_terminate(
        self, input: ITSystemTerminateInput
    ) -> Response[ITSystem]:
        return uuid2response(await terminate_itsystem(input.to_pydantic()), ITUserRead)

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

    @strawberry.mutation(
        description="Refresh ITSystems.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("itsystem"),
        ],
    )
    async def itsystem_refresh(
        self,
        info: Info,
        filter: ITSystemFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(it_system_resolver, ITSystem)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="itsystem", exchange=exchange, owner=owner
        )

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
        description="Creates a list of itusers.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("ituser"),
        ],
    )
    async def itusers_create(
        self, input: list[ITUserCreateInput]
    ) -> list[Response[ITUser]]:
        created_itusers = await asyncio.gather(
            *[Mutation.ituser_create(self, ituser) for ituser in input]
        )
        return created_itusers

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
    async def ituser_terminate(
        self, input: ITUserTerminateInput
    ) -> Response[ITUser]:  # pragma: no cover
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

    @strawberry.mutation(
        description="Refresh IT-Users.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("ituser"),
        ],
    )
    async def ituser_refresh(
        self,
        info: Info,
        filter: ITUserFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(it_user_resolver, ITUser)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="ituser", exchange=exchange, owner=owner
        )

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

    @strawberry.mutation(
        description="Refresh KLEs.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("kle"),
        ],
    )
    async def kle_refresh(
        self,
        info: Info,
        filter: KLEFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(kle_resolver, KLE)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="kle", exchange=exchange, owner=owner
        )

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

    @strawberry.mutation(
        description="Refresh leaves.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("leave"),
        ],
    )
    async def leave_refresh(
        self,
        info: Info,
        filter: LeaveFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(leave_resolver, Leave)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="leave", exchange=exchange, owner=owner
        )

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
        description="Creates a list of managers.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("manager"),
        ],
    )
    async def managers_create(
        self, input: list[ManagerCreateInput]
    ) -> list[Response[Manager]]:
        created_managers = await asyncio.gather(
            *[Mutation.manager_create(self, manager) for manager in input]
        )
        return created_managers

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

    @strawberry.mutation(
        description="Refresh managers.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("manager"),
        ],
    )
    async def manager_refresh(
        self,
        info: Info,
        filter: ManagerFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(manager_resolver, Manager)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="manager", exchange=exchange, owner=owner
        )

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
        # coverage: pause
        return await info.context["org_loader"].load(0)
        # coverage: unpause

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
        self, info: Info, input: OrganisationUnitUpdateInput
    ) -> Response[OrganisationUnit]:
        return uuid2response(
            await update_org_unit(version=get_version(info.schema), input=input),
            OrganisationUnitRead,
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

    @strawberry.mutation(
        description="Refresh organization units.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("org_unit"),
        ],
    )
    async def org_unit_refresh(
        self,
        info: Info,
        filter: OrganisationUnitFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(organisation_unit_resolver, OrganisationUnit)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="org_unit", exchange=exchange, owner=owner
        )

    # Owner
    # -------------
    @strawberry.mutation(
        description="Creates an owner.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("owner"),
        ],
    )
    async def owner_create(self, input: OwnerCreateInput) -> Response[Owner]:
        return uuid2response(await create_owner(input.to_pydantic()), OwnerRead)

    @strawberry.mutation(
        description="Updates an owner.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("owner"),
        ],
    )
    async def owner_update(self, input: OwnerUpdateInput) -> Response[Owner]:
        return uuid2response(await update_owner(input.to_pydantic()), OwnerRead)

    @strawberry.mutation(
        description="Terminates an owner.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("owner"),
        ],
    )
    async def owner_terminate(self, input: OwnerTerminateInput) -> Response[Owner]:
        return uuid2response(await terminate_owner(input.to_pydantic()), OwnerRead)

    # TODO: owner_delete

    @strawberry.mutation(
        description="Refresh owners.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("owner"),
        ],
    )
    async def owner_refresh(
        self,
        info: Info,
        filter: OwnerFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(owner_resolver, Owner)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info, page=page, model="owner", exchange=exchange, owner=owner
        )

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

    @strawberry.mutation(
        description="Refresh a related unit.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("related_unit"),
        ],
    )
    async def related_unit_refresh(
        self,
        info: Info,
        filter: RelatedUnitFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(related_unit_resolver, RelatedUnit)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info,
            page=page,
            model="related_unit",
            exchange=exchange,
            owner=owner,
        )

    # Rolebindings
    # ------------

    @strawberry.mutation(
        description="Create a rolebinding.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("rolebinding"),
        ],
    )
    async def rolebinding_create(
        self, input: RoleBindingCreateInput
    ) -> Response[RoleBinding]:
        return uuid2response(
            await create_rolebinding(input.to_pydantic()), RoleBindingRead
        )

    @strawberry.mutation(
        description="Creates a list of rolebindings.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("rolebinding"),
        ],
    )
    async def rolebindings_create(
        self, input: list[RoleBindingCreateInput]
    ) -> list[Response[RoleBinding]]:
        created_rolebindings = await asyncio.gather(
            *[Mutation.rolebinding_create(self, rolebinding) for rolebinding in input]
        )
        return created_rolebindings

    @strawberry.mutation(
        description="Update a rolebinding.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("rolebinding"),
        ],
    )
    async def rolebinding_update(
        self, input: RoleBindingUpdateInput
    ) -> Response[RoleBinding]:
        return uuid2response(
            await update_rolebinding(input.to_pydantic()), RoleBindingRead
        )

    @strawberry.mutation(
        description="Terminate a rolebinding.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("rolebinding"),
        ],
    )
    async def rolebinding_terminate(
        self, input: RoleBindingTerminateInput
    ) -> Response[RoleBinding]:
        return uuid2response(
            await terminate_rolebinding(input.to_pydantic()), RoleBindingRead
        )

    # TODO: roles_delete

    @strawberry.mutation(
        description="Refresh rolebindings.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_refresh_permission("rolebinding"),
        ],
    )
    async def rolebinding_refresh(
        self,
        info: Info,
        filter: RoleBindingFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        queue: QueueType = None,
        exchange: str | None = None,
        owner: UUID | None = None,
    ) -> Paged[UUID]:
        resolve = to_paged_uuids(rolebinding_resolver, RoleBindingRead)
        page = await resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
        return await refresh(
            info=info,
            page=page,
            model="rolebinding",
            exchange=exchange,
            owner=owner,
        )

    # Event system
    # ------------
    @strawberry.mutation(
        description=dedent(
            """\
            Create a namespace.

            This operation is idempotent, so it can be called upon application startup.

            Namespaces are used to create your own event systems.
            """,
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("event_namespace"),
        ],
    )
    async def event_namespace_declare(
        self, info: Info, input: NamespaceCreateInput
    ) -> Namespace:
        session: AsyncSession = info.context["session"]
        owner = get_authenticated_user()

        stmt = (
            pg_insert(db.Namespace)
            .values(
                name=input.name,
                owner=owner,
                public=input.public,
            )
            .on_conflict_do_nothing()
        )

        await session.execute(stmt)

        # coverage: pause
        namespace = await session.scalar(
            select(db.Namespace).where(db.Namespace.name == input.name)
        )
        # Namespace was either created or it already exists
        assert namespace is not None

        if namespace.owner != owner:
            raise ValueError("Namespace already claimed by another owner.")

        if namespace.public != input.public:
            raise ValueError(
                f"Namespace already exists with public={str(namespace.public).lower()}."
            )

        return Namespace(
            name=namespace.name,
            owner=namespace.owner,
            public=namespace.public,
        )
        # coverage: unpause

    @strawberry.mutation(
        description=dedent(
            """\
            Delete a namespace.

            Use `event_listener_delete` first, if there are any listeners.
            """,
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("event_namespace"),
        ],
    )
    async def event_namespace_delete(
        self,
        info: Info,
        input: NamespaceDeleteInput,
    ) -> bool:
        session: AsyncSession = info.context["session"]

        # coverage: pause
        try:
            await session.execute(
                delete(db.Namespace).where(db.Namespace.name == input.name)
            )
        except sqlalchemy.exc.IntegrityError:  # pragma: no cover
            raise ValueError(
                "There are still listeners for this namespace. Use the `event_listener_delete` mutator."
            )
        return True
        # coverage: unpause

    @strawberry.mutation(
        description=dedent(
            """\
            Create a listener.

            This operation is idempotent, so it can always be called upon application startup.

            Use different user_keys to listen for the same (namespace, routing_key) multiple times. The user_key must be unique for each listener in your integration.
            """,
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("event_listener"),
        ],
    )
    async def event_listener_declare(
        self, info: Info, input: ListenerCreateInput
    ) -> Listener:
        session: AsyncSession = info.context["session"]
        owner = get_authenticated_user()

        namespace = await session.scalar(
            select(db.Namespace).where(db.Namespace.name == input.namespace)
        )

        # coverage: pause
        if namespace is None:
            raise ValueError("Namespace does not exist")

        if namespace.public is False and namespace.owner != owner:
            raise ValueError(
                "Namespace already exists, but is non-public and you are not the owner."
            )

        stmt = (
            pg_insert(db.Listener)
            .values(
                user_key=input.user_key,
                owner=owner,
                namespace_fk=input.namespace,
                routing_key=input.routing_key,
            )
            .on_conflict_do_nothing()
        )

        await session.execute(stmt)

        listener = await session.scalar(
            select(db.Listener).where(
                db.Listener.user_key == input.user_key,
                db.Listener.namespace_fk == input.namespace,
            )
        )
        # Listener was either created or it already exists
        assert listener is not None

        if listener.routing_key != input.routing_key:
            raise ValueError(
                "There already exists a listener with this user_key and a different routing_key"
            )

        return Listener(
            uuid=listener.pk,
            owner=listener.owner,
            user_key=listener.user_key,
            routing_key=listener.routing_key,
            namespace_fk=listener.namespace_fk,
        )
        # coverage: unpause

    @strawberry.mutation(
        description="Delete a listener.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_delete_permission("event_listener"),
        ],
    )
    async def event_listener_delete(
        self,
        info: Info,
        input: ListenerDeleteInput,
    ) -> bool:
        session: AsyncSession = info.context["session"]

        # coverage: pause
        if input.delete_pending_events:
            await session.execute(
                delete(db.Event).where(db.Event.listener_fk == input.uuid)
            )

        try:
            await session.execute(
                delete(db.Listener).where(db.Listener.pk == input.uuid)
            )
        except sqlalchemy.exc.IntegrityError:  # pragma: no cover
            raise ValueError(
                "There are pending events for this listener. Consider carefully if these need to be handled first. You can delete the listener anyway with `delete_pending_events`."
            )
        return True
        # coverage: unpause

    @strawberry.mutation(
        description="Acknowledge an event.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("acknowledge_event"),
        ],
    )
    async def event_acknowledge(
        self,
        info: Info,
        input: EventAcknowledgeInput,
    ) -> bool:
        owner = get_authenticated_user()
        session: AsyncSession = info.context["session"]

        # Sadly, we have to select the listener, because PostgreSQL does not
        # support returning values from tables other than the one being deleted
        listener = await session.scalar(
            select(db.Listener)
            .join(db.Event)
            .where(
                db.Event.pk == input.token.uuid,
            )
        )

        # coverage: pause
        if not listener:
            return True

        result = await session.execute(
            delete(db.Event).where(
                db.Event.listener_fk == db.Listener.pk,
                db.Event.pk == input.token.uuid,
                db.Event.generation == input.token.generation,
                db.Listener.owner == owner,
            )
        )

        if result.rowcount:
            METRIC_ACKNOWLEDGED_EVENTS.labels(
                owner=listener.owner,
                user_key=listener.user_key,
                namespace=listener.namespace_fk,
                routing_key=listener.routing_key,
            ).inc()
        return True
        # coverage: unpause

    @strawberry.mutation(
        description="Send an event.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("send_event"),
        ],
    )
    async def event_send(
        self,
        info: Info,
        input: EventSendInput,
    ) -> bool:
        if input.priority < 1:
            raise ValueError("priority must be natural")

        # This is an arbitrary constraint because we don't want to end up with
        # large amounts of data being sent over the event system.
        if len(input.subject) > 220:
            raise ValueError(
                "Too large subject. Only send identifiers as the subject, not data"
            )

        # coverage: pause
        session: AsyncSession = info.context["session"]
        namespace = await session.scalar(
            select(db.Namespace).where(db.Namespace.name == input.namespace)
        )
        if namespace is None:
            raise ValueError("Namespace does not exist.")
        if namespace.owner != get_authenticated_user():
            raise ValueError("You are not the owner of that namespace.")

        await add_event(
            session,
            namespace=input.namespace,
            routing_key=input.routing_key,
            subject=input.subject,
            priority=input.priority,
        )
        return True
        # coverage: unpause

    @strawberry.mutation(
        description=dedent(
            """\
            Silence an event.

            In general, this should only be done by humans while the implementation of a fix is in the works.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("silence_event"),
        ],
    )
    async def event_silence(
        self,
        info: Info,
        input: EventSilenceInput,
    ) -> bool:
        # coverage: pause
        session: AsyncSession = info.context["session"]
        await session.execute(
            update(db.Event)
            .where(
                db.Event.subject.in_(input.subjects),
                db.Event.listener_fk == db.Listener.pk,
                *input.listeners.where_clauses(),
            )
            .values(silenced=True)
        )
        return True
        # coverage: unpause

    @strawberry.mutation(
        description="Unsilence all matching events",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("unsilence_event"),
        ],
    )
    async def event_unsilence(
        self,
        info: Info,
        input: EventUnsilenceInput,
    ) -> bool:
        clauses = [
            db.Event.listener_fk == db.Listener.pk,
        ]

        if input.listeners is not None:
            clauses.extend(input.listeners.where_clauses())

        if input.subjects is not None:
            clauses.append(db.Event.subject.in_(input.subjects))

        if input.priorities is not None:  # pragma: no cover
            clauses.append(db.Event.priority.in_(input.priorities))

        # coverage: pause
        session: AsyncSession = info.context["session"]
        await session.execute(update(db.Event).where(*clauses).values(silenced=False))
        return True
        # coverage: unpause

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

        # coverage: pause
        return "OK"
        # coverage: unpause


async def delete_bruger(uuid: UUID) -> UUID:
    """Delete a user by creating a "Slettet" (deleted) registration."""
    c = get_connector()
    uuid = await c.bruger.delete(uuid)
    # coverage: pause
    return uuid
    # coverage: unpause


async def delete_organisationfunktion(uuid: UUID) -> UUID:
    """Delete an organisationfunktion by creating a "Slettet" (deleted) registration."""
    c = get_connector()
    uuid = await c.organisationfunktion.delete(uuid)
    # coverage: pause
    return uuid
    # coverage: unpause


async def refresh(
    info: Info,
    page: Paged[UUID],
    model: str,
    exchange: str | None,
    owner: UUID | None,
) -> Paged[UUID]:
    """Publish AMQP messages for UUIDs in the page, optionally to a specific exchange."""
    # Publish UUIDs to AMQP
    uuids = page.objects

    # coverage: pause
    if owner is None:
        amqp_system = info.context["amqp_system"]
        tasks = (
            amqp_system.publish_message(
                routing_key=model,
                payload=str(uuid),
                # Broadcasts on OS2mo's default exchange (usually 'os2mo') if None
                exchange=exchange,
            )
            for uuid in uuids
        )
        await gather_with_concurrency(100, *tasks)

    if owner is not None and exchange is None:
        session: AsyncSession = info.context["session"]
        for uuid in uuids:
            await add_event(
                session,
                namespace="mo",
                routing_key=model,
                subject=str(uuid),
                listener_owner=owner,
            )

    if owner is None and exchange is None or owner is not None and exchange is not None:
        raise ValueError("You must refresh with and owner or an exchange")

    # Return the page to reduce duplicated boilerplate in the callers
    return page
    # coverage: unpause
