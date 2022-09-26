# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import cast

import strawberry
from pydantic import parse_obj_as
from strawberry.types import Info

from .health import health_map
from .models import ConfigurationRead
from .models import FileRead
from .models import FileStore
from .models import HealthRead
from .permissions import gen_read_permission
from .resolvers import EmployeeResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import Resolver
from .resolvers import StaticResolver
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
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version
from mora.config import get_public_settings


@strawberry.type(description="Entrypoint for all read-operations")
class Query:
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: list[Response[Address]] = strawberry.field(
        resolver=Resolver("address_getter", "address_loader").resolve,
        description="Get a list of all addresses, optionally by uuid(s)",
        permission_classes=[gen_read_permission("addresses")],
    )

    # Associations
    # ------------
    associations: list[Response[Association]] = strawberry.field(
        resolver=Resolver("association_getter", "association_loader").resolve,
        description="Get a list of all Associations, optionally by uuid(s)",
        permission_classes=[gen_read_permission("associations")],
    )

    # Classes
    # -------
    classes: list[Class] = strawberry.field(
        resolver=StaticResolver("class_getter", "class_loader").resolve,
        description="Get a list of all classes, optionally by uuid(s)",
        permission_classes=[gen_read_permission("classes")],
    )

    # Employees
    # ---------
    employees: list[Response[Employee]] = strawberry.field(
        resolver=EmployeeResolver().resolve,
        description="Get a list of all employees, optionally by uuid(s)",
        permission_classes=[gen_read_permission("employees")],
    )

    # Engagements
    # -----------
    engagements: list[Response[Engagement]] = strawberry.field(
        resolver=Resolver("engagement_getter", "engagement_loader").resolve,
        description="Get a list of all engagements, optionally by uuid(s)",
        permission_classes=[gen_read_permission("engagements")],
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: list[Response[EngagementAssociation]] = strawberry.field(
        resolver=Resolver(
            "engagement_association_getter", "engagement_association_loader"
        ).resolve,
        description="Get a list of engagement associations",
        permission_classes=[gen_read_permission("engagement_associations")],
    )

    # Facets
    # ------
    facets: list[Facet] = strawberry.field(
        resolver=StaticResolver("facet_getter", "facet_loader").resolve,
        description="Get a list of all facets, optionally by uuid(s)",
        permission_classes=[gen_read_permission("facets")],
    )

    # ITSystems
    # ---------
    itsystems: list[ITSystem] = strawberry.field(
        resolver=StaticResolver("itsystem_getter", "itsystem_loader").resolve,
        description="Get a list of all ITSystems, optionally by uuid(s)",
        permission_classes=[gen_read_permission("itsystems")],
    )

    # ITUsers
    # -------
    itusers: list[Response[ITUser]] = strawberry.field(
        resolver=Resolver("ituser_getter", "ituser_loader").resolve,
        description="Get a list of all ITUsers, optionally by uuid(s)",
        permission_classes=[gen_read_permission("itusers")],
    )

    # KLEs
    # ----
    kles: list[Response[KLE]] = strawberry.field(
        resolver=Resolver("kle_getter", "kle_loader").resolve,
        description="Get a list of all KLE's, optionally by uuid(s)",
        permission_classes=[gen_read_permission("kles")],
    )

    # Leave
    # -----
    leaves: list[Response[Leave]] = strawberry.field(
        resolver=Resolver("leave_getter", "leave_loader").resolve,
        description="Get a list of all leaves, optionally by uuid(s)",
        permission_classes=[gen_read_permission("leaves")],
    )

    # Managers
    # --------
    managers: list[Response[Manager]] = strawberry.field(
        resolver=Resolver("manager_getter", "manager_loader").resolve,
        description="Get a list of all managers, optionally by uuid(s)",
        permission_classes=[gen_read_permission("managers")],
    )

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
        permission_classes=[gen_read_permission("org")],
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Organisational Units
    # --------------------
    org_units: list[Response[OrganisationUnit]] = strawberry.field(
        resolver=OrganisationUnitResolver().resolve,
        description="Get a list of all organisation units, optionally by uuid(s)",
        permission_classes=[gen_read_permission("org_units")],
    )

    # Related Units
    # -------------
    related_units: list[Response[RelatedUnit]] = strawberry.field(
        resolver=Resolver("rel_unit_getter", "rel_unit_loader").resolve,
        description="Get a list of related organisation units, optionally by uuid(s)",
        permission_classes=[gen_read_permission("related_units")],
    )

    # Roles
    # -----
    roles: list[Response[Role]] = strawberry.field(
        resolver=Resolver("role_getter", "role_loader").resolve,
        description="Get a list of all roles, optionally by uuid(s)",
        permission_classes=[gen_read_permission("roles")],
    )

    # Version
    # -------
    @strawberry.field(
        description="Get component versions",
        permission_classes=[gen_read_permission("version")],
    )
    async def version(self) -> Version:
        return Version()

    # Health
    # ------
    @strawberry.field(
        description="Get a list of all health checks, optionally by identifier(s)",
        permission_classes=[gen_read_permission("healths")],
    )
    async def healths(self, identifiers: list[str] | None = None) -> list[Health]:
        healthchecks = set(health_map.keys())
        if identifiers is not None:
            healthchecks = healthchecks.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"identifier": identifier}

        healths = list(map(construct, healthchecks))
        parsed_healths = parse_obj_as(list[HealthRead], healths)
        return list(map(Health.from_pydantic, parsed_healths))

    # Files
    # -----
    @strawberry.field(
        description="Get a list of all files, optionally by filename(s)",
        permission_classes=[gen_read_permission("files")],
    )
    async def files(
        self, info: Info, file_store: FileStore, file_names: list[str] | None = None
    ) -> list[File]:
        filestorage = info.context["filestorage"]
        found_files = filestorage.list_files(file_store)
        if file_names is not None:
            found_files = found_files.intersection(set(file_names))

        def construct(file_name: str) -> dict[str, Any]:
            return {"file_store": file_store, "file_name": file_name}

        files = list(map(construct, found_files))
        parsed_files = parse_obj_as(list[FileRead], files)
        return list(map(File.from_pydantic, parsed_files))

    # Configuration
    # -------------
    @strawberry.field(
        description="Get a list of configuration variables.",
        permission_classes=[gen_read_permission("configuration")],
    )
    async def configuration(
        self, identifiers: list[str] | None = None
    ) -> list[Configuration]:
        settings_keys = get_public_settings()
        if identifiers is not None:
            settings_keys = settings_keys.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"key": identifier}

        settings = list(map(construct, settings_keys))
        parsed_settings = parse_obj_as(list[ConfigurationRead], settings)
        return cast(list[Configuration], parsed_settings)
