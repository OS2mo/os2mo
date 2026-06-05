# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from textwrap import dedent
from typing import cast

import strawberry
from strawberry.types import Info

from mora import db
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.graphapi.context import MOInfo
from mora.graphapi.fields import Metadata
from mora.graphapi.gmodels.mo.details.association import AssociationRead
from mora.graphapi.gmodels.mo.details.engagement import EngagementRead
from mora.graphapi.gmodels.mo.details.it_system import ITSystemRead
from mora.graphapi.gmodels.mo.details.it_system import ITUserRead
from mora.graphapi.gmodels.mo.details.kle import KLERead
from mora.graphapi.gmodels.mo.details.leave import LeaveRead
from mora.graphapi.gmodels.mo.details.manager import ManagerRead
from mora.graphapi.gmodels.mo.details.owner import OwnerRead
from mora.graphapi.gmodels.mo.details.related_unit import RelatedUnitRead
from mora.graphapi.gmodels.mo.employee import EmployeeRead
from mora.graphapi.gmodels.mo.organisation_unit import OrganisationUnitRead
from mora.graphapi.version import Version as GraphQLVersion

from .access_log import AccessLog
from .access_log import access_log_resolver
from .actor import Myself
from .actor import myself_resolver
from .collections import KLE
from .collections import Address
from .collections import Association
from .collections import Class
from .collections import Employee
from .collections import Engagement
from .collections import Facet
from .collections import File
from .collections import Health
from .collections import ITSystem
from .collections import ITUser
from .collections import Leave
from .collections import Manager
from .collections import Organisation
from .collections import OrganisationUnit
from .collections import Owner
from .collections import RelatedUnit
from .collections import RoleBinding
from .collections import Version
from .collections.utils import paged_to_response
from .events import Event
from .events import FullEvent
from .events import Listener
from .events import Namespace
from .events import event_resolver
from .events import full_event_resolver
from .events import listener_resolver
from .events import namespace_resolver
from .filters import FileFilter
from .filters import HealthFilter
from .health import health_map
from .model_registration import IRegistration
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .paged import CursorType
from .paged import LimitType
from .paged import PageHelper
from .paged import Paged
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .permissions import gen_role_permission
from .registrationbase import Registration
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
from .resolvers import registration_resolver
from .resolvers import related_unit_resolver
from .resolvers import rolebinding_resolver
from .response import Response

async def health_resolver(
    info: Info,
    filter: HealthFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Paged[Health]:
    if filter is None:
        filter = HealthFilter()

    healthchecks = set(health_map.keys())
    if filter.identifiers is not None:
        healthchecks = healthchecks.intersection(set(filter.identifiers))

    pag = PageHelper(filter, cursor, limit)
    health_list = sorted(healthchecks)
    if limit is not None:
        healths = health_list[pag.offset : pag.offset + limit]
    else:
        healths = health_list[pag.offset:]

    health_objects = [
        Health(identifier=identifier)  # type: ignore[call-arg]
        for identifier in healths
    ]
    has_more = bool(healths) if limit is not None else False
    return pag.paged(health_objects, has_more=has_more)


async def file_resolver(
    info: MOInfo,
    filter: FileFilter,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Paged[File]:
    if filter is None:  # pragma: no cover
        filter = FileFilter()

    session: AsyncSession = info.context.session
    access_log(
        session,
        "file_resolver",
        "File",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        [],
    )

    found_files = await db.files.ls(session, filter)
    pag = PageHelper(filter, cursor, limit)
    file_list = sorted(found_files) if isinstance(found_files, set) else list(found_files)
    if limit is not None:
        files = file_list[pag.offset : pag.offset + limit]
    else:
        files = file_list[pag.offset:]

    file_objects = [
        File(file_store=filter.file_store, file_name=file_name)  # type: ignore[call-arg]
        for file_name in files
    ]
    has_more = bool(files) if limit is not None else False
    return pag.paged(file_objects, has_more=has_more)


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=paged_to_response(address_resolver, AddressRead),
        description="Get addresses.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=paged_to_response(association_resolver, AssociationRead),
        description="Get associations.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: Paged[Response[Class]] = strawberry.field(
        resolver=paged_to_response(class_resolver, ClassRead),
        description="Get classes.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=paged_to_response(employee_resolver, EmployeeRead),
        description="Get employees.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'persons' instead. Will be removed in a future version of OS2mo.",
    )
    persons: Paged[Response[Employee]] = strawberry.field(
        resolver=paged_to_response(employee_resolver, EmployeeRead),
        description="Get persons.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=paged_to_response(engagement_resolver, EngagementRead),
        description="Get engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=paged_to_response(facet_resolver, FacetRead),
        description="Get facets.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=paged_to_response(it_system_resolver, ITSystemRead),
        description="Get it-systems.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=paged_to_response(it_user_resolver, ITUserRead),
        description="Get it-users.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=paged_to_response(kle_resolver, KLERead),
        description="Get kles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=paged_to_response(leave_resolver, LeaveRead),
        description="Get leaves.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=paged_to_response(manager_resolver, ManagerRead),
        description="Get manager roles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Owners
    # ------
    owners: Paged[Response[Owner]] = strawberry.field(
        resolver=paged_to_response(owner_resolver, OwnerRead),
        description="Get owners.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=paged_to_response(organisation_unit_resolver, OrganisationUnitRead),
        description="Get organisation units.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=paged_to_response(related_unit_resolver, RelatedUnitRead),
        description="Get related organisation units.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    rolebindings: Paged[Response[RoleBinding]] = strawberry.field(
        resolver=paged_to_response(rolebinding_resolver, RoleBindingRead),
        description="Get role-mappings.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("rolebinding"),
        ],
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=health_resolver,
        description="Query healthcheck status.",
        permission_classes=[],
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=file_resolver,
        description="Fetch files from the configured file backend (if any).",
        deprecation_reason="The file-store functionality will be removed in a future version of OS2mo.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    registrations__v25: Paged[Registration] = strawberry.field(
        name="registrations",
        resolver=registration_resolver,
        description=dedent(
            """\
            Get a list of registrations.

            Mostly useful for auditing purposes seeing when data-changes were made and by whom.

            **Warning**:
            This entry should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("registration"),
        ],
        metadata=Metadata(version=lambda v: v <= GraphQLVersion.VERSION_25),
    )
    registrations__v26: Paged[IRegistration] = strawberry.field(
        name="registrations",
        resolver=registration_resolver,
        description=dedent(
            """\
            Get a list of registrations.

            Mostly useful for auditing purposes seeing when data-changes were made and by whom.

            **Warning**:
            This entry should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("registration"),
        ],
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_26),
    )

    access_log: Paged[AccessLog] = strawberry.field(
        resolver=access_log_resolver,
        description=dedent(
            """\
            Get a list of access events.

            Mostly useful for auditing purposes seeing when data was read and by whom.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("accesslog"),
        ],
    )

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=dedent(
            """\
            Get the root organisation.

            This endpoint fails if not exactly one exists in LoRa.
            """
        ),
        deprecation_reason="The root organisation concept will be removed in a future version of OS2mo.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org")],
    )
    async def org(self, info: MOInfo) -> Organisation:
        return cast(Organisation, await info.context.dataloaders.org_loader.load(0))

    # Version
    # -------
    @strawberry.field(
        description="Get component versions of OS2mo.",
        permission_classes=[],
    )
    async def version(self) -> Version:
        return Version()

    # Event system
    # ------------

    events: Paged[FullEvent] = strawberry.field(
        resolver=full_event_resolver,
        description=dedent(
            """\
            Get full events.

            FullEvents represent Events, but they do not have a token for acknowledgement.

            Use `event_fetch` for event-driven applications.

            This collection is intended for inspection by humans.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event"),
        ],
    )

    event_namespaces: Paged[Namespace] = strawberry.field(
        resolver=namespace_resolver,
        description="Get event namespaces.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_namespace"),
        ],
    )

    event_listeners: Paged[Listener] = strawberry.field(
        resolver=listener_resolver,
        description="Get event listeners.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_listener"),
        ],
    )

    event_fetch: Event | None = strawberry.field(
        resolver=event_resolver,
        description=dedent(
            """\
            Get an event.

            `event_fetch` is a key operation for event-driven integrations.

            Fetched events must be acknowledged by the consumer after it has been processed.

            Consumers cannot rely on the order of events, and may receive the same event multiple times.
            """,
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_role_permission("fetch_event"),
        ],
    )

    me: Myself = strawberry.field(
        resolver=myself_resolver,
        description=dedent(
            """\
            Get information about the API client itself (i.e. the current caller).

            This collection allows clients to query information about themselves, such
            as their configured actor UUID, RBAC roles, login / contact email address,
            created event namespaces and listeners, etc.
            """,
        ),
        permission_classes=[IsAuthenticatedPermission],
    )
