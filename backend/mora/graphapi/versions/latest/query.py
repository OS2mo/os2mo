# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Any
from typing import Any
from typing import Any
from typing import Any
from typing import cast
from typing import Optional
from typing import Optional
from typing import Optional

import strawberry
from pydantic import parse_obj_as
from pydantic import parse_obj_as
from pydantic import parse_obj_as
from strawberry.types import Info

from mora.config import get_public_settings
from mora.graphapi.versions.latest.files import list_files
from mora.graphapi.versions.latest.health import health_map
from mora.graphapi.versions.latest.models import ConfigurationRead
from mora.graphapi.versions.latest.models import FileRead
from mora.graphapi.versions.latest.models import FileStore
from mora.graphapi.versions.latest.models import HealthRead
from mora.graphapi.versions.latest.resolvers import EmployeeResolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.resolvers import StaticResolver
from mora.graphapi.versions.latest.resolvers import StaticResolver
from mora.graphapi.versions.latest.resolvers import StaticResolver
from mora.graphapi.versions.latest.schema import Address
from mora.graphapi.versions.latest.schema import Association
from mora.graphapi.versions.latest.schema import Class
from mora.graphapi.versions.latest.schema import Configuration
from mora.graphapi.versions.latest.schema import Configuration
from mora.graphapi.versions.latest.schema import Employee
from mora.graphapi.versions.latest.schema import Engagement
from mora.graphapi.versions.latest.schema import EngagementAssociation
from mora.graphapi.versions.latest.schema import Facet
from mora.graphapi.versions.latest.schema import File
from mora.graphapi.versions.latest.schema import File
from mora.graphapi.versions.latest.schema import Health
from mora.graphapi.versions.latest.schema import Health
from mora.graphapi.versions.latest.schema import ITSystem
from mora.graphapi.versions.latest.schema import ITUser
from mora.graphapi.versions.latest.schema import KLE
from mora.graphapi.versions.latest.schema import Leave
from mora.graphapi.versions.latest.schema import Manager
from mora.graphapi.versions.latest.schema import Organisation
from mora.graphapi.versions.latest.schema import OrganisationUnit
from mora.graphapi.versions.latest.schema import RelatedUnit
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Response
from mora.graphapi.versions.latest.schema import Role
from mora.graphapi.versions.latest.schema import Version
from mora.graphapi.versions.latest.schema import Version


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
    )

    # Associations
    # ---------
    associations: list[Response[Association]] = strawberry.field(
        resolver=Resolver("association_getter", "association_loader").resolve,
        description="Get a list of all Associations, optionally by uuid(s)",
    )

    # Classes
    # -------
    classes: list[Class] = strawberry.field(
        resolver=StaticResolver("class_getter", "class_loader").resolve,
        description="Get a list of all classes, optionally by uuid(s)",
    )

    # Employees
    # ---------
    employees: list[Response[Employee]] = strawberry.field(
        resolver=EmployeeResolver().resolve,
        description="Get a list of all employees, optionally by uuid(s)",
    )

    # Engagements
    # -----------
    engagements: list[Response[Engagement]] = strawberry.field(
        resolver=Resolver("engagement_getter", "engagement_loader").resolve,
        description="Get a list of all engagements, optionally by uuid(s)",
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: list[Response[EngagementAssociation]] = strawberry.field(
        resolver=Resolver(
            "engagement_association_getter", "engagement_association_loader"
        ).resolve,
        description="Get a list of engagement associations",
    )

    # Facets
    # ------
    facets: list[Facet] = strawberry.field(
        resolver=StaticResolver("facet_getter", "facet_loader").resolve,
        description="Get a list of all facets, optionally by uuid(s)",
    )

    # ITSystems
    # ---------
    itsystems: list[ITSystem] = strawberry.field(
        resolver=StaticResolver("itsystem_getter", "itsystem_loader").resolve,
        description="Get a list of all ITSystems, optionally by uuid(s)",
    )

    # ITUsers
    # -------
    itusers: list[Response[ITUser]] = strawberry.field(
        resolver=Resolver("ituser_getter", "ituser_loader").resolve,
        description="Get a list of all ITUsers, optionally by uuid(s)",
    )

    # KLEs
    # ----
    kles: list[Response[KLE]] = strawberry.field(
        resolver=Resolver("kle_getter", "kle_loader").resolve,
        description="Get a list of all KLE's, optionally by uuid(s)",
    )

    # Leave
    # -----
    leaves: list[Response[Leave]] = strawberry.field(
        resolver=Resolver("leave_getter", "leave_loader").resolve,
        description="Get a list of all leaves, optionally by uuid(s)",
    )

    # Managers
    # --------
    managers: list[Response[Manager]] = strawberry.field(
        resolver=Resolver("manager_getter", "manager_loader").resolve,
        description="Get a list of all managers, optionally by uuid(s)",
    )

    # Root Organisation
    # -----------------
    @strawberry.field(
        description=(
            "Get the root-organisation. "
            "This endpoint fails if not exactly one exists in LoRa."
        ),
    )
    async def org(self, info: Info) -> Organisation:
        return await info.context["org_loader"].load(0)

    # Organisational Units
    # --------------------
    org_units: list[Response[OrganisationUnit]] = strawberry.field(
        resolver=Resolver("org_unit_getter", "org_unit_loader").resolve,
        description="Get a list of all organisation units, optionally by uuid(s)",
    )

    # Related Units
    # ---------
    related_units: list[Response[RelatedUnit]] = strawberry.field(
        resolver=Resolver("rel_unit_getter", "rel_unit_loader").resolve,
        description="Get a list of related organisation units, optionally by uuid(s)",
    )

    # Roles
    # ---------
    roles: list[Response[Role]] = strawberry.field(
        resolver=Resolver("role_getter", "role_loader").resolve,
        description="Get a list of all roles, optionally by uuid(s)",
    )

    # Version
    # -------
    @strawberry.field(
        description="Get component versions",
    )
    async def version(self) -> Version:
        return Version()

    # Health
    # ------
    @strawberry.field(
        description="Get a list of all health checks, optionally by identifier(s)",
    )
    async def healths(self, identifiers: Optional[list[str]] = None) -> list[Health]:
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
    )
    async def files(
        self, file_store: FileStore, file_names: Optional[list[str]] = None
    ) -> list[File]:
        found_files = list_files(file_store)
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
    )
    async def configuration(
        self, identifiers: Optional[list[str]] = None
    ) -> list[Configuration]:
        settings_keys = get_public_settings()
        if identifiers is not None:
            settings_keys = settings_keys.intersection(set(identifiers))

        def construct(identifier: Any) -> dict[str, Any]:
            return {"key": identifier}

        settings = list(map(construct, settings_keys))
        parsed_settings = parse_obj_as(list[ConfigurationRead], settings)
        return cast(list[Configuration], parsed_settings)
