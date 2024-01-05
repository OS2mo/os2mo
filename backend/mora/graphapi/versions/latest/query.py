# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import partial
from functools import wraps
from textwrap import dedent
from typing import Any
from typing import TypeVar
from uuid import UUID

import strawberry
from starlette_context import context
from strawberry.types import Info

from .audit import audit_log_resolver
from .audit import AuditLog
from .filters import ConfigurationFilter
from .filters import FileFilter
from .filters import HealthFilter
from .health import health_map
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .registration import Registration
from .registration import registration_resolver
from .resolvers import address_resolver
from .resolvers import association_resolver
from .resolvers import class_resolver
from .resolvers import CursorType
from .resolvers import employee_resolver
from .resolvers import engagement_resolver
from .resolvers import facet_resolver
from .resolvers import it_system_resolver
from .resolvers import it_user_resolver
from .resolvers import kle_resolver
from .resolvers import leave_resolver
from .resolvers import LimitType
from .resolvers import manager_resolver
from .resolvers import organisation_unit_resolver
from .resolvers import owner_resolver
from .resolvers import PagedResolver
from .resolvers import related_unit_resolver
from .resolvers import role_resolver
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
from .schema import Paged
from .schema import PageInfo
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version
from .types import Cursor
from mora.audit import audit_log
from mora.config import get_public_settings
from mora.util import now


T = TypeVar("T")


def paginate(obj: list[T], cursor: CursorType, limit: LimitType) -> list[T]:
    if cursor is None:
        return obj[:limit]
    return obj[cursor.offset :][:limit]


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


class FileResolver(PagedResolver):
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


def to_func_response(model: Any, result: dict[UUID, list[dict]]) -> list[Response]:
    return [
        Response(uuid=uuid, model=model, object_cache=objects)  # type: ignore[call-arg]
        for uuid, objects in result.items()
    ]


def to_func_uuids(model: Any, result: dict[UUID, list[dict]]) -> list[UUID]:
    return list(result.keys())


def to_paged(resolver: PagedResolver, result_transformer: Callable[[PagedResolver, Any], list[Any]] | None = None):  # type: ignore
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver.resolve)
    async def resolve_response(*args, limit: LimitType, cursor: CursorType, **kwargs):  # type: ignore
        if limit and cursor is None:
            cursor = Cursor(
                offset=0,
                registration_time=str(now()),
            )

        result = await resolver.resolve(*args, limit=limit, cursor=cursor, **kwargs)

        end_cursor: CursorType = None
        if limit and cursor is not None:
            end_cursor = Cursor(
                offset=cursor.offset + limit,
                registration_time=cursor.registration_time,
            )
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(resolver, result),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response


def to_paged_func(resolver_func: Callable, model: Any, result_transformer: Any | None = None):  # type: ignore
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver_func)
    async def resolve_response(*args, limit: LimitType, cursor: CursorType, **kwargs):  # type: ignore
        if limit and cursor is None:
            cursor = Cursor(
                offset=0,
                registration_time=str(now()),
            )

        result = await resolver_func(*args, limit=limit, cursor=cursor, **kwargs)

        end_cursor: CursorType = None
        if limit and cursor is not None:
            end_cursor = Cursor(
                offset=cursor.offset + limit,
                registration_time=cursor.registration_time,
            )
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(  # type: ignore[call-arg]
            objects=result_transformer(model, result),
            page_info=PageInfo(next_cursor=end_cursor),  # type: ignore[call-arg]
        )

    return resolve_response


to_paged_func_response = partial(to_paged_func, result_transformer=to_func_response)
to_paged_func_uuids = partial(to_paged_func, result_transformer=to_func_uuids)


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=to_paged_func_response(address_resolver, Address),
        description="Get addresses.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=to_paged_func_response(association_resolver, Association),
        description="Get associations.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: Paged[Response[Class]] = strawberry.field(
        resolver=to_paged_func_response(class_resolver, Class),
        description="Get classes.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=to_paged_func_response(employee_resolver, Employee),
        description="Get employees.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=to_paged_func_response(engagement_resolver, Engagement),
        description="Get engagements.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=to_paged_func_response(facet_resolver, Facet),
        description="Get facets.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=to_paged_func_response(it_system_resolver, ITSystem),
        description="Get it-systems.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=to_paged_func_response(it_user_resolver, ITUser),
        description="Get it-users.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=to_paged_func_response(kle_resolver, KLE),
        description="Get kles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=to_paged_func_response(leave_resolver, Leave),
        description="Get leaves.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=to_paged_func_response(manager_resolver, Manager),
        description="Get manager roles.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Owners
    # ------
    owners: Paged[Response[Owner]] = strawberry.field(
        resolver=to_paged_func_response(owner_resolver, Owner),
        description="Get owners.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=to_paged_func_response(organisation_unit_resolver, OrganisationUnit),
        description="Get organisation units.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=to_paged_func_response(related_unit_resolver, RelatedUnit),
        description="Get related organisation units.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    roles: Paged[Response[Role]] = strawberry.field(
        resolver=to_paged_func_response(role_resolver, Role),
        description="Get role-mappings.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=to_paged_func(health_resolver, Health),
        description="Query healthcheck status.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("health")],
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=to_paged(FileResolver()),
        description="Fetch files from the configured file backend (if any).",
        deprecation_reason="The file-store functionality will be removed in a future version of OS2mo.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    # Configuration
    # -------------
    configuration: Paged[Configuration] = strawberry.field(
        resolver=to_paged(ConfigurationResolver()),
        description="Get configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )

    registrations: Paged[Registration] = strawberry.field(
        resolver=to_paged_func(registration_resolver, Registration),
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
        resolver=to_paged_func(audit_log_resolver, AuditLog),
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
