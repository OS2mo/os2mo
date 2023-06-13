# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import partial
from functools import wraps
from typing import Any
from typing import cast
from uuid import UUID

import strawberry
from pydantic import parse_obj_as
from starlette_context import context
from strawberry.types import Info

from .health import health_map
from .models import ConfigurationRead
from .models import FileRead
from .models import FileStore
from .models import HealthRead
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .resolvers import EmployeeResolver
from .resolvers import EngagementAssociationResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import ITSystemResolver
from .resolvers import ITUserResolver
from .resolvers import KLEResolver
from .resolvers import LeaveResolver
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import PagedResolver
from .resolvers import RelatedUnitResolver
from .resolvers import Resolver
from .resolvers import RoleResolver
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Configuration
from .schema import Employee
from .schema import Engagement
from .schema import EngagementAssociation
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
from .schema import Paged
from .schema import PageInfo
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version
from .types import Cursor
from mora.config import get_public_settings


class HealthResolver(PagedResolver):
    async def resolve(  # type: ignore[override]
        self,
        limit: int | None = None,
        cursor: Cursor | None = None,
        identifiers: list[str] | None = None,
    ) -> list[Health]:
        healthchecks = set(health_map.keys())
        if identifiers is not None:
            healthchecks = healthchecks.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"identifier": identifier}

        healths = list(map(construct, healthchecks))
        healths = healths[cursor:][:limit]
        if not healths:
            context["lora_page_out_of_range"] = True
        parsed_healths = parse_obj_as(list[HealthRead], healths)
        return list(map(Health.from_pydantic, parsed_healths))


class FileResolver(PagedResolver):
    async def resolve(  # type: ignore[override]
        self,
        info: Info,
        file_store: FileStore,
        limit: int | None = None,
        cursor: Cursor | None = None,
        file_names: list[str] | None = None,
    ) -> list[File]:
        filestorage = info.context["filestorage"]
        found_files = filestorage.list_files(file_store)
        if file_names is not None:
            found_files = found_files.intersection(set(file_names))

        def construct(file_name: str) -> dict[str, Any]:
            return {"file_store": file_store, "file_name": file_name}

        files = list(map(construct, found_files))
        files = files[cursor:][:limit]
        if not files:
            context["lora_page_out_of_range"] = True

        parsed_files = parse_obj_as(list[FileRead], files)
        return list(map(File.from_pydantic, parsed_files))


class ConfigurationResolver(PagedResolver):
    async def resolve(  # type: ignore[override]
        self,
        limit: int | None = None,
        cursor: Cursor | None = None,
        identifiers: list[str] | None = None,
    ) -> list[Configuration]:
        settings_keys = get_public_settings()
        if identifiers is not None:
            settings_keys = settings_keys.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"key": identifier}

        settings = list(map(construct, settings_keys))
        settings = settings[cursor:][:limit]
        if not settings:
            context["lora_page_out_of_range"] = True

        parsed_settings = parse_obj_as(list[ConfigurationRead], settings)
        return cast(list[Configuration], parsed_settings)


def to_response(resolver: Resolver, result: dict[UUID, list[dict]]) -> list[Response]:
    return [
        Response(uuid=uuid, model=resolver.model, object_cache=objects)
        for uuid, objects in result.items()
    ]


def to_paged(resolver: PagedResolver, result_transformer: Callable[[PagedResolver, Any], list[Any]] | None = None):  # type: ignore
    result_transformer = result_transformer or (lambda _, x: x)

    @wraps(resolver.resolve)
    async def resolve_response(*args, limit: int | None, cursor: Cursor | None, **kwargs):  # type: ignore
        result = await resolver.resolve(*args, limit=limit, cursor=cursor, **kwargs)

        end_cursor: int | None = None
        if limit:
            end_cursor = (cursor or 0) + limit
        if context.get("lora_page_out_of_range"):
            end_cursor = None

        assert result_transformer is not None
        return Paged(
            objects=result_transformer(resolver, result),
            page_info=PageInfo(next_cursor=end_cursor),
        )

    return resolve_response


to_paged_response = partial(to_paged, result_transformer=to_response)


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: Paged[Response[Address]] = strawberry.field(
        resolver=to_paged_response(AddressResolver()),
        description="Get a list of all addresses, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: Paged[Response[Association]] = strawberry.field(
        resolver=to_paged_response(AssociationResolver()),
        description="Get a list of all Associations, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: Paged[Response[Class]] = strawberry.field(
        resolver=to_paged_response(ClassResolver()),
        description="Get a list of all classes, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: Paged[Response[Employee]] = strawberry.field(
        resolver=to_paged_response(EmployeeResolver()),
        description="Get a list of all employees, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: Paged[Response[Engagement]] = strawberry.field(
        resolver=to_paged_response(EngagementResolver()),
        description="Get a list of all engagements, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: Paged[Response[EngagementAssociation]] = strawberry.field(
        resolver=to_paged_response(EngagementAssociationResolver()),
        description="Get a list of engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )

    # Facets
    # ------
    facets: Paged[Response[Facet]] = strawberry.field(
        resolver=to_paged_response(FacetResolver()),
        description="Get a list of all facets, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: Paged[Response[ITSystem]] = strawberry.field(
        resolver=to_paged_response(ITSystemResolver()),
        description="Get a list of all ITSystems, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: Paged[Response[ITUser]] = strawberry.field(
        resolver=to_paged_response(ITUserResolver()),
        description="Get a list of all ITUsers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: Paged[Response[KLE]] = strawberry.field(
        resolver=to_paged_response(KLEResolver()),
        description="Get a list of all KLE's, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: Paged[Response[Leave]] = strawberry.field(
        resolver=to_paged_response(LeaveResolver()),
        description="Get a list of all leaves, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: Paged[Response[Manager]] = strawberry.field(
        resolver=to_paged_response(ManagerResolver()),
        description="Get a list of all managers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Organisational Units
    # --------------------
    org_units: Paged[Response[OrganisationUnit]] = strawberry.field(
        resolver=to_paged_response(OrganisationUnitResolver()),
        description="Get a list of all organisation units, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: Paged[Response[RelatedUnit]] = strawberry.field(
        resolver=to_paged_response(RelatedUnitResolver()),
        description="Get a list of related organisation units, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    roles: Paged[Response[Role]] = strawberry.field(
        resolver=to_paged_response(RoleResolver()),
        description="Get a list of all roles, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    # Health
    # ------
    healths: Paged[Health] = strawberry.field(
        resolver=to_paged(HealthResolver()),
        description="Get a list of all health checks, optionally by identifier(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("health")],
    )

    # Files
    # -----
    files: Paged[File] = strawberry.field(
        resolver=to_paged(FileResolver()),
        description="Get a list of all files, optionally by filename(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    # Configuration
    # -------------
    configuration: Paged[Configuration] = strawberry.field(
        resolver=to_paged(ConfigurationResolver()),
        description="Get a list of configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root organisation\n"
            "\n"
            "This endpoint fails if not exactly one exists in LoRa."
        ),
        deprecation_reason="The root organisation concept will be removed in a future version of OS2mo",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org")],
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Version
    # -------
    @strawberry.field(
        description="Get component versions",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("version")],
    )
    async def version(self) -> Version:
        return Version()
