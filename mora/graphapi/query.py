# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from textwrap import dedent
from typing import TypeVar
from typing import cast
from uuid import UUID

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
from .collections.utils import to_paged_response
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
from .paged import ObjectsAndCursor
from .paged import Paged
from .paged import to_paged
from .policies import Policy
from .policies import policy_resolver
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
from .types import Cursor

T = TypeVar("T")


async def health_resolver(
    info: Info,
    filter: HealthFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:
        filter = HealthFilter()

    healthchecks = set(health_map.keys())
    if filter.identifiers is not None:
        healthchecks = healthchecks.intersection(set(filter.identifiers))

    offset = int(cursor.last) if cursor else 0
    healths = sorted(healthchecks)[offset:][:limit]
    return ObjectsAndCursor(
        objects=[
            Health(identifier=identifier)  # type: ignore[call-arg]
            for identifier in healths
        ],
        next_cursor=(
            Cursor(last=UUID(int=offset + limit)) if limit and healths else None
        ),
    )


async def file_resolver(
    info: MOInfo,
    filter: FileFilter,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> ObjectsAndCursor:
    if filter is None:  # pragma: no cover
        filter = FileFilter()

    session: AsyncSession = info.context.session
    # We do not need the access log elsewhere for files, because this is the
    # only way to resolve a `File` (which is needed to read the content).
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

    offset = int(cursor.last) if cursor else 0
    files = sorted(found_files)[offset:][:limit]

    return ObjectsAndCursor(
        objects=[
            File(file_store=filter.file_store, file_name=file_name)  # type: ignore[call-arg]
            for file_name in files
        ],
        next_cursor=(
            Cursor(last=UUID(int=offset + limit)) if limit and files else None
        ),
    )


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=to_paged_response(AddressRead)(address_resolver),
        description="Get addresses.",
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=to_paged_response(AssociationRead)(association_resolver),
        description="Get associations.",
    )

    # Classes
    # -------
    classes: Paged[Response[Class]] = strawberry.field(
        resolver=to_paged_response(ClassRead)(class_resolver),
        description="Get classes.",
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=to_paged_response(EmployeeRead)(employee_resolver),
        description="Get employees.",
        deprecation_reason="Use 'persons' instead. Will be removed in a future version of OS2mo.",
    )
    persons: Paged[Response[Employee]] = strawberry.field(
        resolver=to_paged_response(EmployeeRead)(employee_resolver),
        description="Get persons.",
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=to_paged_response(EngagementRead)(engagement_resolver),
        description="Get engagements.",
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=to_paged_response(FacetRead)(facet_resolver),
        description="Get facets.",
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=to_paged_response(ITSystemRead)(it_system_resolver),
        description="Get it-systems.",
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=to_paged_response(ITUserRead)(it_user_resolver),
        description="Get it-users.",
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=to_paged_response(KLERead)(kle_resolver),
        description="Get kles.",
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=to_paged_response(LeaveRead)(leave_resolver),
        description="Get leaves.",
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=to_paged_response(ManagerRead)(manager_resolver),
        description="Get manager roles.",
    )

    # Owners
    # ------
    owners: Paged[Response[Owner]] = strawberry.field(
        resolver=to_paged_response(OwnerRead)(owner_resolver),
        description="Get owners.",
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=to_paged_response(OrganisationUnitRead)(organisation_unit_resolver),
        description="Get organisation units.",
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=to_paged_response(RelatedUnitRead)(related_unit_resolver),
        description="Get related organisation units.",
    )

    # Roles
    # -----
    rolebindings: Paged[Response[RoleBinding]] = strawberry.field(
        resolver=to_paged_response(RoleBindingRead)(rolebinding_resolver),
        description="Get role-mappings.",
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=to_paged(health_resolver),
        description="Query healthcheck status.",
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=to_paged(file_resolver),
        description="Fetch files from the configured file backend (if any).",
        deprecation_reason="The file-store functionality will be removed in a future version of OS2mo.",
    )

    registrations__v25: Paged[Registration] = strawberry.field(
        name="registrations",
        resolver=to_paged(registration_resolver),
        description=dedent(
            """\
            Get a list of registrations.

            Mostly useful for auditing purposes seeing when data-changes were made and by whom.

            **Warning**:
            This entry should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        metadata=Metadata(version=lambda v: v <= GraphQLVersion.VERSION_25),
    )
    registrations__v26: Paged[IRegistration] = strawberry.field(
        name="registrations",
        resolver=to_paged(registration_resolver),
        description=dedent(
            """\
            Get a list of registrations.

            Mostly useful for auditing purposes seeing when data-changes were made and by whom.

            **Warning**:
            This entry should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_26),
    )

    access_log: Paged[AccessLog] = strawberry.field(
        resolver=to_paged(access_log_resolver),
        description=dedent(
            """\
            Get a list of access events.

            Mostly useful for auditing purposes seeing when data was read and by whom.
            """
        ),
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
    )
    async def org(self, info: MOInfo) -> Organisation:
        return cast(Organisation, await info.context.dataloaders.org_loader.load(0))

    # Version
    # -------
    @strawberry.field(
        description="Get component versions of OS2mo.",
    )
    async def version(self) -> Version:
        return Version()

    # Event system
    # ------------

    events: Paged[FullEvent] = strawberry.field(
        resolver=to_paged(full_event_resolver),
        description=dedent(
            """\
            Get full events.

            FullEvents represent Events, but they do not have a token for acknowledgement.

            Use `event_fetch` for event-driven applications.

            This collection is intended for inspection by humans.
            """
        ),
    )

    event_namespaces: Paged[Namespace] = strawberry.field(
        resolver=to_paged(namespace_resolver),
        description="Get event namespaces.",
    )

    event_listeners: Paged[Listener] = strawberry.field(
        resolver=to_paged(listener_resolver),
        description="Get event listeners.",
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
    )

    policies: Paged[Policy] = strawberry.field(
        resolver=to_paged(policy_resolver),
        description="Get access policies.",
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
    )
