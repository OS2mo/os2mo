# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Like latest, but with schema models from this version, with old resolvers."""
from textwrap import dedent

import strawberry
from strawberry.types import Info

from ..latest.permissions import gen_read_permission
from ..latest.permissions import IsAuthenticatedPermission
from .registration import Registration
from .registration import RegistrationResolver
from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .resolvers import ConfigurationResolver
from .resolvers import EmployeeResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import FileResolver
from .resolvers import HealthResolver
from .resolvers import ITSystemResolver
from .resolvers import ITUserResolver
from .resolvers import KLEResolver
from .resolvers import LeaveResolver
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import OwnerResolver
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
from .schema import Paged
from .schema import RelatedUnit
from .schema import Response
from .schema import Role
from .schema import Version


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
        permission_classes=[IsAuthenticatedPermission],
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
