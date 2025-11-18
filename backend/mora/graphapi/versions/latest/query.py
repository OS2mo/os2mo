# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from textwrap import dedent
from typing import Any
from typing import TypeVar
from uuid import UUID
from .lazy import LazyClass

import strawberry
from starlette_context import context
from strawberry.types import Info

from mora import db
from mora.access_log import access_log
from mora.config import get_public_settings
from mora.db import AsyncSession
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

from .access_log import AccessLog
from .access_log import access_log_resolver
from .actor import Myself
from .actor import myself_resolver
from .events import Event
from .events import FullEvent
from .events import Listener
from .events import Namespace
from .events import event_resolver
from .events import full_event_resolver
from .events import listener_resolver
from .events import namespace_resolver
from .filters import ConfigurationFilter
from .filters import FileFilter
from .filters import HealthFilter
from .health import health_map
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .paged import CursorType
from .paged import LimitType
from .paged import Paged
from .paged import to_paged
from .permissions import IsAuthenticatedPermission
from .permissions import gen_read_permission
from .permissions import gen_role_permission
from .registration import Registration
from .registration import registration_resolver
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
from .response import Response
from .schema import KLE
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Configuration
from .schema import Employee
from .schema import Engagement
from .schema import Facet
from .schema import File
from .schema import Health
from .schema import ITSystem
from .schema import ITUser
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import Owner
from .schema import RelatedUnit
from .schema import RoleBinding
from .schema import Version

T = TypeVar("T")


def paginate(obj: list[T], cursor: CursorType, limit: LimitType) -> list[T]:
    if cursor is None:
        return obj[:limit]
    # coverage: pause
    return obj[cursor.offset :][:limit]
    # coverage: unpause


async def health_resolver(
    filter: HealthFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[Health]:
    if filter is None:
        filter = HealthFilter()

    healthchecks = set(health_map.keys())
    if filter.identifiers is not None:
        healthchecks = healthchecks.intersection(set(filter.identifiers))

    healths = paginate(list(healthchecks), cursor, limit)
    if not healths:
        context["lora_page_out_of_range"] = True
    return [
        Health(identifier=identifier)  # type: ignore[call-arg]
        for identifier in healths
    ]


async def file_resolver(
    info: Info,
    filter: FileFilter,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[File]:
    if filter is None:  # pragma: no cover
        filter = FileFilter()

    session: AsyncSession = info.context["session"]
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

    files = paginate(list(found_files), cursor, limit)
    if not files:
        context["lora_page_out_of_range"] = True

    return [
        File(file_store=filter.file_store, file_name=file_name)  # type: ignore[call-arg]
        for file_name in files
    ]


async def configuration_resolver(
    filter: ConfigurationFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[Configuration]:
    if filter is None:
        filter = ConfigurationFilter()

    settings_keys = get_public_settings()
    if filter.identifiers is not None:
        settings_keys = settings_keys.intersection(set(filter.identifiers))

    settings = paginate(list(settings_keys), cursor, limit)
    if not settings:  # pragma: no cover
        context["lora_page_out_of_range"] = True

    return [Configuration(key=key) for key in settings]  # type: ignore[call-arg]


def to_func_response(model: Any, result: dict[UUID, list[dict]]) -> list[Response]:
    return [
        Response[model](uuid=uuid, object_cache=objects)
        for uuid, objects in result.items()
    ]


def to_func_uuids(model: Any, result: dict[UUID, list[dict]]) -> list[UUID]:
    return list(result.keys())


to_paged_response = partial(to_paged, result_transformer=to_func_response)
to_paged_uuids = partial(to_paged, result_transformer=to_func_uuids)


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=to_paged_response(address_resolver, AddressRead),
        description="Get addresses.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=to_paged_response(association_resolver, AssociationRead),
        description="Get associations.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response(class_resolver, ClassRead),
        description="Get classes.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=to_paged_response(employee_resolver, EmployeeRead),
        description="Get employees.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=to_paged_response(engagement_resolver, EngagementRead),
        description="Get engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=to_paged_response(facet_resolver, FacetRead),
        description="Get facets.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=to_paged_response(it_system_resolver, ITSystemRead),
        description="Get it-systems.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=to_paged_response(it_user_resolver, ITUserRead),
        description="Get it-users.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=to_paged_response(kle_resolver, KLERead),
        description="Get kles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=to_paged_response(leave_resolver, LeaveRead),
        description="Get leaves.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=to_paged_response(manager_resolver, ManagerRead),
        description="Get manager roles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Owners
    # ------
    owners: Paged[Response[Owner]] = strawberry.field(
        resolver=to_paged_response(owner_resolver, OwnerRead),
        description="Get owners.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=to_paged_response(organisation_unit_resolver, OrganisationUnitRead),
        description="Get organisation units.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=to_paged_response(related_unit_resolver, RelatedUnitRead),
        description="Get related organisation units.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    rolebindings: Paged[Response[RoleBinding]] = strawberry.field(
        resolver=to_paged_response(rolebinding_resolver, RoleBindingRead),
        description="Get role-mappings.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("rolebinding"),
        ],
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=to_paged(health_resolver, Health),
        description="Query healthcheck status.",
        permission_classes=[],
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=to_paged(file_resolver, File),
        description="Fetch files from the configured file backend (if any).",
        deprecation_reason="The file-store functionality will be removed in a future version of OS2mo.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    # Configuration
    # -------------
    configuration: Paged[Configuration] = strawberry.field(
        resolver=to_paged(configuration_resolver, Configuration),
        description="Get configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )

    registrations: Paged[Registration] = strawberry.field(
        resolver=to_paged(registration_resolver, Registration),
        description=dedent(
            """\
            Get a list of registrations.

            Mostly useful for auditing purposes seeing when data-changes were made and by whom.

            **Warning**:
            This entry should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the AMQP-based event-system.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("registration"),
        ],
    )

    access_log: Paged[AccessLog] = strawberry.field(
        resolver=to_paged(access_log_resolver, AccessLog),
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
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

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
        resolver=to_paged(full_event_resolver, FullEvent),
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
        resolver=to_paged(namespace_resolver, Namespace),
        description="Get event namespaces.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("event_namespace"),
        ],
    )

    event_listeners: Paged[Listener] = strawberry.field(
        resolver=to_paged(listener_resolver, Listener),
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
