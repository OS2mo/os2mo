# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import wraps
from inspect import Parameter
from inspect import signature
from typing import Any

import strawberry
from more_itertools import flatten
from pydantic import PositiveInt

from ..latest.permissions import gen_read_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..latest.query import to_paged
from ..latest.types import Cursor
from ..v13.query import ConfigurationResolver
from ..v13.query import FileResolver
from ..v13.query import HealthResolver
from ..v13.resolvers import AddressResolver
from ..v13.resolvers import AssociationResolver
from ..v13.resolvers import ClassResolver
from ..v13.resolvers import EmployeeResolver
from ..v13.resolvers import EngagementAssociationResolver
from ..v13.resolvers import EngagementResolver
from ..v13.resolvers import FacetResolver
from ..v13.resolvers import ITSystemResolver
from ..v13.resolvers import ITUserResolver
from ..v13.resolvers import KLEResolver
from ..v13.resolvers import LeaveResolver
from ..v13.resolvers import ManagerResolver
from ..v13.resolvers import OrganisationUnitResolver
from ..v13.resolvers import RelatedUnitResolver
from ..v13.resolvers import RoleResolver
from ..v13.schema import Address
from ..v13.schema import Association
from ..v13.schema import Class
from ..v13.schema import Configuration
from ..v13.schema import Employee
from ..v13.schema import Engagement
from ..v13.schema import EngagementAssociation
from ..v13.schema import Facet
from ..v13.schema import File
from ..v13.schema import Health
from ..v13.schema import ITSystem
from ..v13.schema import ITUser
from ..v13.schema import KLE
from ..v13.schema import Leave
from ..v13.schema import Manager
from ..v13.schema import OrganisationUnit
from ..v13.schema import Paged
from ..v13.schema import RelatedUnit
from ..v13.schema import Response
from ..v13.schema import Role
from ..v5.version import GraphQLVersion as NextGraphQLVersion


def to_response(resolver):  # type: ignore
    @wraps(resolver.resolve)
    async def resolve_response(*args, **kwargs):  # type: ignore
        result = await resolver.resolve(*args, **kwargs)
        return [
            Response(uuid=uuid, model=resolver.model, object_cache=objects)
            for uuid, objects in result.items()
        ]

    return resolve_response


def to_list(resolver):  # type: ignore
    @wraps(resolver.resolve)
    async def resolve_response(*args, **kwargs):  # type: ignore
        result = await resolver.resolve(*args, **kwargs)
        return list(flatten(result.values()))

    return resolve_response


def offset2cursor(func: Callable) -> Callable:
    sig = signature(func)
    parameters = sig.parameters.copy()
    del parameters["cursor"]
    parameter_list = list(parameters.values())
    parameter_list.append(
        Parameter(
            "offset",
            Parameter.POSITIONAL_OR_KEYWORD,
            annotation=PositiveInt | None,
            default=None,
        )
    )
    new_sig = sig.replace(parameters=parameter_list)

    async def cursor_func(*args: Any, offset: PositiveInt | None, **kwargs: Any) -> Any:
        cursor = Cursor(offset) if offset is not None else None
        return await func(*args, cursor=cursor, **kwargs)

    cursor_func.__signature__ = new_sig  # type: ignore[attr-defined]
    return cursor_func


@strawberry.type(description="Entrypoint for all read-operations")
class Query(NextGraphQLVersion.schema.query):  # type: ignore[name-defined]
    """Query is the top-level entrypoint for all read-operations.

    Operations are listed hereunder using @strawberry.field, grouped by their model.

    Most of the endpoints here are implemented by simply calling their dataloaders.
    """

    # Addresses
    # ---------
    addresses: list[Response[Address]] = strawberry.field(
        resolver=offset2cursor(to_response(AddressResolver())),
        description="Get a list of all addresses, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    # Associations
    # ------------
    associations: list[Response[Association]] = strawberry.field(
        resolver=offset2cursor(to_response(AssociationResolver())),
        description="Get a list of all Associations, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    # Classes
    # -------
    classes: list[Class] = strawberry.field(
        resolver=offset2cursor(to_list(ClassResolver())),
        description="Get a list of all classes, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # Employees
    # ---------
    employees: list[Response[Employee]] = strawberry.field(
        resolver=offset2cursor(to_response(EmployeeResolver())),
        description="Get a list of all employees, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # Engagements
    # -----------
    engagements: list[Response[Engagement]] = strawberry.field(
        resolver=offset2cursor(to_response(EngagementResolver())),
        description="Get a list of all engagements, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    # EngagementsAssociations
    # -----------
    engagement_associations: list[Response[EngagementAssociation]] = strawberry.field(
        resolver=offset2cursor(to_response(EngagementAssociationResolver())),
        description="Get a list of engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )

    # Facets
    # ------
    facets: list[Facet] = strawberry.field(
        resolver=offset2cursor(to_list(FacetResolver())),
        description="Get a list of all facets, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    # ITSystems
    # ---------
    itsystems: list[ITSystem] = strawberry.field(
        resolver=offset2cursor(to_list(ITSystemResolver())),
        description="Get a list of all ITSystems, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    # ITUsers
    # -------
    itusers: list[Response[ITUser]] = strawberry.field(
        resolver=offset2cursor(to_response(ITUserResolver())),
        description="Get a list of all ITUsers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    # KLEs
    # ----
    kles: list[Response[KLE]] = strawberry.field(
        resolver=offset2cursor(to_response(KLEResolver())),
        description="Get a list of all KLE's, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    # Leave
    # -----
    leaves: list[Response[Leave]] = strawberry.field(
        resolver=offset2cursor(to_response(LeaveResolver())),
        description="Get a list of all leaves, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # Managers
    # --------
    managers: list[Response[Manager]] = strawberry.field(
        resolver=offset2cursor(to_response(ManagerResolver())),
        description="Get a list of all managers, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    # Organisational Units
    # --------------------
    org_units: list[Response[OrganisationUnit]] = strawberry.field(
        resolver=offset2cursor(to_response(OrganisationUnitResolver())),
        description="Get a list of all organisation units, optionally by uuid(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # Related Units
    # -------------
    related_units: list[Response[RelatedUnit]] = strawberry.field(
        resolver=offset2cursor(to_response(RelatedUnitResolver())),
        description="Get a list of related organisation units, optionally by uuid(s)",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    # Roles
    # -----
    roles: list[Response[Role]] = strawberry.field(
        resolver=offset2cursor(to_response(RoleResolver())),
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
    files: list[File] = strawberry.field(
        resolver=FileResolver().resolve,
        description="Get a list of all files, optionally by filename(s)",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("file")],
    )

    # Configuration
    # -------------
    configuration: list[Configuration] = strawberry.field(
        resolver=ConfigurationResolver().resolve,
        description="Get a list of configuration variables.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("configuration"),
        ],
    )


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 4 of the GraphQL Schema.

    Version 5 introduced a breaking change to the entire reading schema, by introducing
    pagination on all top-level fields.
    Version 4 ensures that the old functionality is still available.
    """

    query = Query


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 4."""

    version = 4
    schema = GraphQLSchema
