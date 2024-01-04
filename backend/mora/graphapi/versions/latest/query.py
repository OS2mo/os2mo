# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from textwrap import dedent
from typing import TypeVar

import strawberry
from starlette_context import context
from strawberry.types import Info

from .audit import AuditLog
from .audit import AuditLogResolver
from .filters import ConfigurationFilter
from .filters import FileFilter
from .filters import HealthFilter
from .health import health_map
from .paged import Paged
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .registration import Registration
from .registration import RegistrationResolver
from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .paged import CursorType
from .resolvers import EmployeeResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import ITSystemResolver
from .resolvers import ITUserResolver
from .resolvers import KLEResolver
from .resolvers import LeaveResolver
from .paged import LimitType
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import OwnerResolver
from .resolvers import PagedResolver
from .resolvers import RelatedUnitResolver
from .resolvers import RoleResolver
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
from .schema import KLE
from .schema import Leave
from .schema import Manager
from .schema import Organisation
from .schema import OrganisationUnit
from .schema import Owner
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version
from mora.audit import audit_log
from mora.config import get_public_settings


T = TypeVar("T")


def paginate(obj: list[T], cursor: CursorType, limit: LimitType) -> list[T]:
    if cursor is None:
        return obj[:limit]
    return obj[cursor.offset :][:limit]


class HealthResolver(PagedResolver):
    async def paged_resolve(self) -> Paged[Health]:
        pass

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: HealthFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
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


class FileResolver(PagedResolver):
    async def paged_resolve(self) -> Paged[File]:
        pass

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: FileFilter,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        if filter is None:
            filter = FileFilter()

        session = info.context["sessionmaker"]()
        async with session.begin():
            audit_log(
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

        filestorage = info.context["filestorage"]
        found_files = filestorage.list_files(filter.file_store)
        if filter.file_names is not None:
            found_files = found_files.intersection(set(filter.file_names))

        files = paginate(list(found_files), cursor, limit)
        if not files:
            context["lora_page_out_of_range"] = True

        return [
            File(file_store=filter.file_store, file_name=file_name)  # type: ignore[call-arg]
            for file_name in files
        ]


class ConfigurationResolver(PagedResolver):
    async def paged_resolve(self) -> Paged[Configuration]:
        pass

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: ConfigurationFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        if filter is None:
            filter = ConfigurationFilter()

        settings_keys = get_public_settings()
        if filter.identifiers is not None:
            settings_keys = settings_keys.intersection(set(filter.identifiers))

        settings = paginate(list(settings_keys), cursor, limit)
        if not settings:
            context["lora_page_out_of_range"] = True

        return [Configuration(key=key) for key in settings]  # type: ignore[call-arg]


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=AddressResolver().paged_resolve,
        description="Get addresses.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=AssociationResolver().paged_resolve,
        description="Get associations.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: Paged[Response[Class]] = strawberry.field(
        resolver=ClassResolver().paged_resolve,
        description="Get classes.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=EmployeeResolver().paged_resolve,
        description="Get employees.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=EngagementResolver().paged_resolve,
        description="Get engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=FacetResolver().paged_resolve,
        description="Get facets.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=ITSystemResolver().paged_resolve,
        description="Get it-systems.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=ITUserResolver().paged_resolve,
        description="Get it-users.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=KLEResolver().paged_resolve,
        description="Get kles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=LeaveResolver().paged_resolve,
        description="Get leaves.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=ManagerResolver().paged_resolve,
        description="Get manager roles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Owners
    # ------
    owners: Paged[Response[Owner]] = strawberry.field(
        resolver=OwnerResolver().paged_resolve,
        description="Get owners.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=OrganisationUnitResolver().paged_resolve,
        description="Get organisation units.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=RelatedUnitResolver().paged_resolve,
        description="Get related organisation units.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    roles: Paged[Response[Role]] = strawberry.field(
        resolver=RoleResolver().paged_resolve,
        description="Get role-mappings.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=HealthResolver().paged_resolve,
        description="Query healthcheck status.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("health")],
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=FileResolver().paged_resolve,
        description="Fetch files from the configured file backend (if any).",
        deprecation_reason="The file-store functionality will be removed in a future version of OS2mo.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    # Configuration
    # -------------
    configuration: Paged[Configuration] = strawberry.field(
        resolver=ConfigurationResolver().paged_resolve,
        description="Get configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )

    registrations: Paged[Registration] = strawberry.field(
        resolver=RegistrationResolver().paged_resolve,
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

    auditlog: Paged[AuditLog] = strawberry.field(
        resolver=AuditLogResolver().paged_resolve,
        description=dedent(
            """\
            Get a list of audit events.

            Mostly useful for auditing purposes seeing when data was read and by whom.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("auditlog")],
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
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("version")],
    )
    async def version(self) -> Version:
        return Version()
