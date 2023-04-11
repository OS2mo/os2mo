# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph."""
import asyncio
import json
import re
from base64 import b64encode
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from inspect import Parameter
from inspect import signature
from itertools import chain
from typing import Any
from typing import cast
from typing import Generic
from typing import Optional
from typing import TypeVar
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from more_itertools import only
from starlette_context import context
from strawberry import UNSET
from strawberry.dataloader import DataLoader
from strawberry.lazy_type import LazyType
from strawberry.types import Info

from .health import health_map
from .models import ConfigurationRead
from .models import FileRead
from .models import HealthRead
from .models import OrganisationUnitRefreshRead
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .resolver_map import resolver_map
from .resolvers import AddressResolver, AssociationResolver, EmployeeResolver, EngagementAssociationResolver, FacetResolver, ITSystemResolver, ITUserResolver, KLEResolver, LeaveResolver, ManagerResolver, RelatedUnitResolver, RoleResolver
from .resolvers import ClassResolver
from .resolvers import EngagementResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import StaticResolver
from .types import Cursor
from mora import common
from mora import config
from mora import lora
from mora.service.address_handler import dar
from mora.service.address_handler import multifield_text
from mora.service.facet import is_class_uuid_primary
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementAssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITSystemRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import RoleRead


MOObject = TypeVar("MOObject")
RootModel = TypeVar("RootModel")
R = TypeVar("R")


def identity(x: R) -> R:
    """Identity function.

    Args:
        x: Random argument.

    Returns:
        `x` completely unmodified.
    """
    return x


def seed_resolver(
    resolver: StaticResolver,
    root_model: RootModel,
    seeds: dict[str, Callable[[RootModel], Any]],
    result_translation: Callable[[Any], R] | None = None,
) -> Callable[..., Awaitable[R]]:
    """Seed the provided top-level resolver to be used in a field-level context.

    This function serves to create a new function which calls the `resolver.resolve`
    method with seeded values from the field-context in which it is called.

    Example:
        A resolver exists to load organisation units, namely `OrganisationUnitResolver`.
        This resolver accepts a `parents` parameter, which given a UUID of an existing
        organisation unit loads all of its children.

        From our top-level `Query` object context, the caller can set this parameter
        explicitly, however on the OrganisationUnit field-level, we would like this
        parameter to be given by the context, i.e. when asking for `children` on an
        organisation unit, we expect the `parent` parameter on the resolver to be set
        to the object we call `children` on.

        This can be achieved by setting `seeds` to a dictionary that sets `parents` to
        a callable that extracts the root object's `uuid` from the object itself:
        ```
        child_count: int = strawberry.field(
            description="Children count of the organisation unit.",
            resolver=seed_resolver(
                OrganisationUnitResolver(),
                OrganisationUnitRead,
                {"parents": lambda root: [root.uuid]},
                lambda result: len(result.keys()),
            ),
            ...
        )
        ```
        In this example a `result_translation` lambda is also used to map from the list
        of OrganisationUnits returned by the resolver to the number of children found.

    Args:
        resolver: The top-level resolver to seed arguments to.
        root_model: The root-model applicable for the field-level context.
        seeds:
            A dictionary mapping from parameter name to callables resolving the argument
            values from the root object.
        result_translation:
            A result translation callable translating the resolver return value
            from one type to another. Uses the identity function if not provided.

    Returns:
        A seeded resolver function that accepts the same parameters as the
        `resolver.resolve` function, except with the `seeds` keys removed as parameters,
        and a `root` parameter with the `root_model` type added.
    """
    # If no result_translation function was provided, default to the identity function.
    result_translation = result_translation or identity

    async def seeded_resolver(*args: Any, root: Any, **kwargs: Any) -> R:
        # Resolve arguments from the root object
        for key, argument_callable in seeds.items():
            kwargs[key] = argument_callable(root)
        result = await resolver.resolve(*args, **kwargs)
        assert result_translation is not None
        return result_translation(result)

    sig = signature(resolver.resolve)
    parameters = sig.parameters.copy()
    # Remove the `seeds` parameters from the parameter list, as these will be resolved
    # from the root object on call-time instead.
    for key in seeds.keys():
        del parameters[key]
    # Add the `root` parameter to the parameter list, as it is required for all the
    # `seeds` resolvers to determine call-time parameters.
    parameter_list = list(parameters.values())
    parameter_list = [Parameter(
        "root", Parameter.POSITIONAL_OR_KEYWORD, annotation=root_model
    )] + parameter_list
    # Generate and apply our new signature to the seeded_resolver function
    new_sig = sig.replace(parameters=parameter_list)
    seeded_resolver.__signature__ = new_sig  # type: ignore[attr-defined]

    return seeded_resolver


# seed_resolver functions pre-seeded with result_translation functions assuming that
# only a single UUID will be returned, converting the objects list to either a list or
# an optional entity.
seed_resolver_list = partial(
    seed_resolver, result_translation=lambda result: list(chain.from_iterable(result.values()))
)
seed_resolver_optional = partial(
    seed_resolver, result_translation=lambda result: only(chain.from_iterable(result.values()))
)
# TODO: Eliminate optional list
seed_resolver_optional_list = partial(
    seed_resolver, result_translation=lambda result: list(chain.from_iterable(result.values())) or None
)
seed_resolver_concrete = partial(
    seed_resolver, result_translation=lambda result: one(chain.from_iterable(result.values()))
)
seed_static_resolver_list = seed_resolver
seed_static_resolver_optional = partial(
    seed_resolver, result_translation=lambda result: only(result)
)
seed_static_resolver_concrete = partial(
    seed_resolver, result_translation=lambda result: one(result)
)


@strawberry.type
class Response(Generic[MOObject]):
    uuid: UUID

    # Object cache is a temporary workaround ensuring that current resolvers keep
    # working as-is while also allowing for lazy resolution based entirely on the UUID.
    object_cache: strawberry.Private[list[MOObject]] = UNSET

    # Due to a limitation in Pythons typing support, it does not seem possible to fetch
    # the concrete class of generics from the generic definition, thus it must be
    # provided explicitly.
    model: strawberry.Private[MOObject]

    @strawberry.field(description="Validities for the current registration")
    async def objects(self, root: Any, info: Info) -> list[MOObject]:
        # If the object_cache is filled our request has already been resolved elsewhere
        if root.object_cache != UNSET:
            return root.object_cache
        # If the object cache has not been filled we must resolve objects using the uuid
        resolver = resolver_map[root.model]["loader"]
        return (await info.context[resolver].load(root.uuid)).object_cache


# Address
# -------


@strawberry.experimental.pydantic.type(
    model=AddressRead,
    all_fields=True,
    description="Address information for an employee or organisation unit",
)
class Address:
    address_type: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            AddressRead,
            {"uuids": lambda root: [root.address_type_uuid]}
        ),
        description="Address type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    visibility: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            AddressRead,
            {"uuids": lambda root: [root.visibility_uuid] if root.visibility_uuid else []}
        ),
        description="Address visibility",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            EmployeeResolver(),
            AddressRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Connected employee. "
        "Note that this is mutually exclusive with the org_unit field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            OrganisationUnitResolver(),
            AddressRead,
            {"uuids": lambda root: [root.org_unit_uuid] if root.org_unit_uuid else []}
        ),
        description="Connected organisation unit. "
        "Note that this is mutually exclusive with the employee field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            EngagementResolver(),
            AddressRead,
            {"uuids": lambda root: [root.engagement_uuid] if root.engagement_uuid else []}
        ),
        description="Connected Engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    @strawberry.field(description="Name of address")
    async def name(self, root: AddressRead, info: Info) -> str | None:
        address_type = await Address.address_type(root=root, info=info)

        if address_type.scope == "MULTIFIELD_TEXT":
            return multifield_text.name(root.value, root.value2)

        if address_type.scope == "DAR":
            dar_loader = context["dar_loader"]
            address_object = await dar_loader.load(UUID(root.value))
            return dar.name_from_dar_object(address_object)

        return root.value

    @strawberry.field(description="href of address")
    async def href(self, root: AddressRead, info: Info) -> str | None:
        address_type = await Address.address_type(root=root, info=info)

        if address_type.scope == "PHONE":
            return f"tel:{root.value}"

        if address_type.scope == "EMAIL":
            return f"mailto:{root.value}"

        if address_type.scope == "DAR":
            dar_loader = context["dar_loader"]
            address_object = await dar_loader.load(UUID(root.value))
            if address_object is None:
                return None
            return dar.open_street_map_href_from_dar_object(address_object)

        return None


async def filter_address_types(
    addresses: list[AddressRead], address_types: list[UUID] | None
) -> list[AddressRead]:
    """Filter a list of addresses based on their address type UUID.

    Args:
        addresses: The addresses to filter
        address_types: The address type UUIDs to filter by.

    Returns:
        list[AddressRead]: Addresses optionally filtered by their address type.
    """
    if address_types is None:
        return addresses
    address_type_list: list[UUID] = address_types
    return list(
        filter(lambda addr: addr.address_type_uuid in address_type_list, addresses)
    )


# Association
# -----------


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    all_fields=True,
    description="Connects organisation units and employees",
)
class Association:
    association_type: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.association_type_uuid] if root.association_type_uuid else []}
        ),
        description="Association type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    dynamic_class: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.dynamic_class_uuid] if root.dynamic_class_uuid else []}
        ),
    )

    primary: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.primary_uuid] if root.primary_uuid else []}
        ),
        description="Primary status",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_concrete(
            OrganisationUnitResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.org_unit_uuid]}
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make optional employee
    substitute: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.substitute_uuid] if root.substitute_uuid else []}
        ),
        description="Connected substitute employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    job_function: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.job_function_uuid] if root.job_function_uuid else []}
        ),
        description="Connected job function",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Can there be more than one ITUser per association?
    it_user: list[LazyType[
        "ITUser", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(),
            AssociationRead,
            {"uuids": lambda root: [root.it_user_uuid] if root.it_user_uuid else []}
        ),
        description="Connected IT user",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )


# Class
# -----


@strawberry.experimental.pydantic.type(
    model=ClassRead,
    all_fields=True,
    description="The value component of the class/facet choice setup",
)
class Class:
    parent: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            ClassRead,
            {"uuids": lambda root: [root.parent_uuid] if root.parent_uuid else []}
        ),
        description="Immediate parent class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    children: list[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver(),
            ClassRead,
            {"parents": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Immediate descendants of the class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    facet: LazyType[
        "Facet", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            FacetResolver(),
            ClassRead,
            {"uuids": lambda root: [root.facet_uuid]}
        ),
        description="Associated facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    @strawberry.field(
        description="Associated top-level facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )
    async def top_level_facet(self, root: ClassRead, info: Info) -> "Facet":
        parent_node: ClassRead = root
        # Traverse class tree
        while parent_node.parent_uuid is not None:
            parent_node = await Class.parent(root=parent_node, info=info)  # type: ignore
        # Return facet for utmost-parent
        return await Class.facet(root=parent_node, info=info)

    @strawberry.field(description="Full name, for backwards compatibility")
    async def full_name(self, root: ClassRead) -> str:
        return root.name


# Employee
# --------


@strawberry.experimental.pydantic.type(
    model=EmployeeRead,
    all_fields=True,
    description="Employee/identity specific information",
)
class Employee:
    @strawberry.field(description="Full name of the employee")
    async def name(self, root: EmployeeRead) -> str:
        return f"{root.givenname} {root.surname}".strip()

    @strawberry.field(description="Full nickname of the employee")
    async def nickname(self, root: EmployeeRead) -> str:
        return f"{root.nickname_givenname} {root.nickname_surname}".strip()

    engagements: list[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Engagements for the employee",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    manager_roles: list[LazyType[
        "Manager", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            ManagerResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Manager roles for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    addresses: list[LazyType[
        "Address", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            AddressResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Addresses for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyType[
        "Leave", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Leaves for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyType[
        "Association", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Associations for the employee",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    roles: list[LazyType[
        "Role", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            RoleResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Roles for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyType[
        "ITUser", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="IT users for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    engagement_associations: list[LazyType[
        "EngagementAssociation", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver(),
            EmployeeRead,
            {"employees": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )


# Engagement
# ----------


@strawberry.experimental.pydantic.type(
    model=EngagementRead,
    all_fields=True,
    description="Employee engagement in an organisation unit",
)
class Engagement:
    engagement_type: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.engagement_type_uuid]}
        ),
        description="Engagement type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    job_function: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.job_function_uuid]}
        ),
        description="Job function",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.primary_uuid] if root.primary_uuid else []}
        ),
        description="Primary status",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    @strawberry.field(description="Is it primary")
    async def is_primary(self, root: EngagementRead, info: Info) -> bool:
        if not root.primary_uuid:
            return False
        # TODO: Eliminate is_class_uuid_primary lookup by using the above resolver
        #       Then utilize is_class_primary as result_translation
        return await is_class_uuid_primary(str(root.primary_uuid))

    leave: Optional[LazyType[
        "Leave", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_optional(
            LeaveResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.leave_uuid] if root.leave_uuid else []}
        ),
        description="Related leave",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            EngagementRead,
            {"uuids": lambda root: [root.org_unit_uuid] if root.org_unit_uuid else []}
        ),
        description="Related organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement_associations: list[LazyType[
        "EngagementAssociation", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver(),
            EngagementRead,
            {"engagements": lambda root: [root.uuid] if root.uuid else []}
        ),
        description="Engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )


# Engagement Association
# ----------


@strawberry.experimental.pydantic.type(
    model=EngagementAssociationRead,
    all_fields=True,
    description="Employee engagement in an organisation unit",
)
class EngagementAssociation:
    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            EngagementAssociationRead,
            {"uuids": lambda root: [root.org_unit_uuid]}
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make concrete engagement
    engagement: list[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver(),
            EngagementAssociationRead,
            {"employees": lambda root: [root.engagement_uuid]}
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement_association_type: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            EngagementAssociationRead,
            {"uuids": lambda root: [root.engagement_association_type_uuid]}
        ),
        description="Related engagement association type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )


# Facet
# -----


@strawberry.experimental.pydantic.type(
    model=FacetRead,
    all_fields=True,
    description="The key component of the class/facet choice setup",
)
class Facet:
    classes: list[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver(),
            FacetRead,
            {"facets": lambda root: [root.uuid]}
        ),
        description="Associated classes",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )


# IT
# --


@strawberry.experimental.pydantic.type(
    model=ITSystemRead,
    all_fields=True,
    description="Systems that IT users are connected to",
)
class ITSystem:
    pass


@strawberry.experimental.pydantic.type(
    model=ITUserRead,
    all_fields=True,
    description="User information related to IT systems",
)
class ITUser:
    # TODO: Remove list, make optional employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            EmployeeResolver(),
            ITUserRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            OrganisationUnitResolver(),
            ITUserRead,
            {"uuids": lambda root: [root.org_unit_uuid] if root.org_unit_uuid else []}
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            EngagementResolver(),
            ITUserRead,
            {"uuids": lambda root: [root.engagement_uuid] if root.engagement_uuid else []}
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    itsystem: LazyType[
        "ITSystem", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ITSystemResolver(),
            ITUserRead,
            {"uuids": lambda root: [root.itsystem_uuid]}
        ),
        description="Connected itsystem",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )


# KLE
# ---


@strawberry.experimental.pydantic.type(
    model=KLERead,
    all_fields=True,
    description="Kommunernes Landsforenings Emnesystematik",
)
class KLE:
    kle_number: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            KLERead,
            {"uuids": lambda root: [root.kle_number_uuid]}
        ),
        description="KLE number",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    kle_aspects: list[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver(),
            KLERead,
            {"uuids": lambda root: root.kle_aspect_uuids if root.kle_aspect_uuids else []}
        ),
        description="KLE Aspects",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            OrganisationUnitResolver(),
            KLERead,
            {"uuids": lambda root: [root.org_unit_uuid] if root.org_unit_uuid else []}
        ),
        description="Associated organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Leave
# -----


@strawberry.experimental.pydantic.type(
    model=LeaveRead,
    all_fields=True,
    description="Leave (e.g. parental leave) for employees",
)
class Leave:
    leave_type: LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ] = strawberry.field(
        resolver=seed_static_resolver_concrete(
            ClassResolver(),
            LeaveRead,
            {"uuids": lambda root: [root.leave_type_uuid]}
        ),
        description="Leave type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(),
            LeaveRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    engagement: Optional[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_optional(
            EngagementResolver(),
            LeaveRead,
            {"employees": lambda root: [root.engagement_uuid]}
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )


# Manager
# -------


@strawberry.experimental.pydantic.type(
    model=ManagerRead,
    all_fields=True,
    description="Managers of organisation units and their connected identities",
)
class Manager:
    manager_type: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            ManagerRead,
            {"uuids": lambda root: [root.manager_type_uuid] if root.manager_type_uuid else []}
        ),
        description="Manager type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    manager_level: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            ManagerRead,
            {"uuids": lambda root: [root.manager_level_uuid] if root.manager_level_uuid else []}
        ),
        description="Manager level",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    responsibilities: list[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver(),
            ManagerRead,
            {"parents": lambda root: root.responsibility_uuids if root.responsibility_uuids else []}
        ),
        description="Manager responsibilities",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyType[
        "Employee", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] | None = strawberry.field(
        resolver=seed_resolver_optional_list(
            EmployeeResolver(),
            ManagerRead,
            {"uuids": lambda root: [root.employee_uuid] if root.employee_uuid else []}
        ),
        description="Manager identity details",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_concrete(
            OrganisationUnitResolver(),
            ManagerRead,
            {"uuids": lambda root: [root.org_unit_uuid]}
        ),
        description="Managed organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Organisation
# ------------


MUNICIPALITY_CODE_PATTERN = re.compile(r"urn:dk:kommune:(\d+)")


@strawberry.experimental.pydantic.type(
    model=OrganisationRead,
    all_fields=True,
    description="Root organisation - one and only one of these can exist",
)
class Organisation:
    @strawberry.field(description="The municipality code for the organisation unit")
    async def municipality_code(
        self, root: OrganisationUnitRead, info: Info
    ) -> int | None:
        """Get The municipality code for the organisation unit (if any).

        Returns:
            The municipality code, if any is found.
        """
        org = await common.get_connector().organisation.get(root.uuid)

        authorities = org.get("relationer", {}).get("myndighed", [])
        for authority in authorities:
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(authority.get("urn"))
            if m:
                return int(m.group(1))
        return None


# Organisation Unit
# -----------------


@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRead,
    all_fields=True,
    description="Hierarchical unit within the organisation tree",
)
class OrganisationUnit:
    parent: Optional[LazyType[
        "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_optional(
            OrganisationUnitResolver(),
            OrganisationUnitRead,
            {"uuids": lambda root: [root.parent_uuid]},
        ),
        description="The immediate descendants in the organisation tree",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    @strawberry.field(
        description="All ancestors in the organisation tree",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )
    async def ancestors(
        self, root: OrganisationUnitRead, info: Info
    ) -> list["OrganisationUnit"]:
        """Get all ancestors in the organisation tree.

        Returns:
            A list of all the ancestors.
        """
        async def rec(root_node: OrganisationUnitRead) -> list["OrganisationUnit"]:
            parent = await OrganisationUnit.parent(root=root_node, info=info)  # type: ignore
            if not parent:
                return []
            return [parent] + await rec(parent)
        return await rec(root)

    children: list[
        LazyType[
            "OrganisationUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
        ]
    ] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            OrganisationUnitRead,
            {"parents": lambda root: [root.uuid]},
        ),
        description="The immediate descendants in the organisation tree",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    child_count: int = strawberry.field(
        resolver=seed_resolver(
            OrganisationUnitResolver(),
            OrganisationUnitRead,
            {"parents": lambda root: [root.uuid]},
            lambda result: len(result.keys()),
        ),
        description="Children count of the organisation unit.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    # TODO: Add _uuid suffix to RAModel and remove _model suffix here
    org_unit_hierarchy_model: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            OrganisationUnitRead,
            {"uuids": lambda root: [root.org_unit_hierarchy] if root.org_unit_hierarchy else []}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    unit_type: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            OrganisationUnitRead,
            {"uuids": lambda root: [root.unit_type_uuid] if root.unit_type_uuid else []}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    org_unit_level: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            OrganisationUnitRead,
            {"uuids": lambda root: [root.org_unit_level_uuid] if root.org_unit_level_uuid else []}
        ),
        description="Organisation unit level",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    time_planning: Optional[LazyType[
        "Class", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_static_resolver_optional(
            ClassResolver(),
            OrganisationUnitRead,
            {"uuids": lambda root: [root.time_planning_uuid] if root.time_planning_uuid else []}
        ),
        description="Time planning strategy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    engagements: list[LazyType[
        "Engagement", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related engagements",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    @strawberry.field(
        description="Managers of the organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )
    async def managers(
        self, root: OrganisationUnitRead, info: Info, inherit: bool = False
    ) -> list["Manager"]:
        loader: DataLoader = info.context["org_unit_manager_loader"]
        ou_loader: DataLoader = info.context["org_unit_loader"]
        result = await loader.load(root.uuid)
        if inherit:
            parent = root
            while not result:
                parent_uuid = parent.parent_uuid
                tasks = [loader.load(parent_uuid), ou_loader.load(parent_uuid)]
                result, response = await asyncio.gather(*tasks)
                potential_parent = only(response, default=None)
                if potential_parent is None:
                    break
                parent = potential_parent
        return result

    addresses: list[LazyType[
        "Address", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            AddressResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related addresses",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyType[
        "Leave", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related leaves",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyType[
        "Association", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    roles: list[LazyType[
        "Role", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            RoleResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related roles",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyType[
        "ITUser", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related IT users",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    kles: list[LazyType[
        "KLE", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            KLEResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="KLE responsibilites for the organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    related_units: list[LazyType[
        "RelatedUnit", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            RelatedUnitResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related units for the organisational unit",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    engagement_associations: list[LazyType[
        "EngagementAssociation", "mora.graphapi.versions.latest.schema"  # noqa: F821
    ]] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver(),
            OrganisationUnitRead,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Engagement associations for the organisational unit",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )


# Related Unit
# ------------


@strawberry.experimental.pydantic.type(
    model=RelatedUnitRead,
    all_fields=True,
    description="list of related organisation units",
)
class RelatedUnit:
    @strawberry.field(
        description="Related organisation units",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )
    async def org_units(
        self, root: RelatedUnitRead, info: Info
    ) -> list["OrganisationUnit"]:
        loader: DataLoader = info.context["org_unit_loader"]
        results = await loader.load_many(root.org_unit_uuids)
        return [one(result) for result in results]


# Role
# ----
@strawberry.experimental.pydantic.type(
    model=RoleRead,
    all_fields=True,
    description="Role an employee has within an organisation unit",
)
class Role:
    @strawberry.field(
        description="Role type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )
    async def role_type(self, root: RoleRead, info: Info) -> "Class":
        loader: DataLoader = info.context["class_loader"]
        return await loader.load(root.role_type_uuid)

    @strawberry.field(
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )
    async def employee(self, root: RoleRead, info: Info) -> list["Employee"]:
        loader: DataLoader = info.context["employee_loader"]
        return await loader.load(root.employee_uuid)

    @strawberry.field(
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )
    async def org_unit(self, root: RoleRead, info: Info) -> list["OrganisationUnit"]:
        loader: DataLoader = info.context["org_unit_loader"]
        return await loader.load(root.org_unit_uuid)


# Health & version
# ----------------
@strawberry.type(description="MO & LoRa & DIPEX versions")
class Version:
    @strawberry.field(description="OS2mo Version")
    async def mo_version(self) -> str | None:
        """Get the mo version.

        Returns:
            The version.
        """
        return config.get_settings().commit_tag

    @strawberry.field(description="OS2mo commit hash")
    async def mo_hash(self) -> str | None:
        """Get the mo commit hash.

        Returns:
            The commit hash.
        """
        return config.get_settings().commit_sha

    @strawberry.field(description="LoRa version")
    async def lora_version(self) -> str | None:
        """Get the lora version.

        Returns:
            The version.
        """
        return await lora.get_version()

    @strawberry.field(description="DIPEX version")
    async def dipex_version(self) -> str | None:
        return config.get_settings().confdb_dipex_version__do_not_use


@strawberry.experimental.pydantic.type(
    model=HealthRead,
    all_fields=True,
    description="Checks whether a specific subsystem is working",
)
class Health:
    @strawberry.field(description="Healthcheck status")
    async def status(self, root: HealthRead) -> bool | None:
        return await health_map[root.identifier]()


T = TypeVar("T")


@strawberry.type
class PageInfo:
    next_cursor: Cursor | None = None


@strawberry.type
class Paged(Generic[T]):
    objects: list[T]
    page_info: PageInfo


# File
# ----
@strawberry.experimental.pydantic.type(
    model=FileRead,
    all_fields=True,
    description="Checks whether a specific subsystem is working",
)
class File:
    @strawberry.field(description="Text contents")
    def text_contents(self, root: FileRead, info: Info) -> str:
        filestorage = info.context["filestorage"]
        return cast(str, filestorage.load_file(root.file_store, root.file_name))

    @strawberry.field(description="Base64 encoded contents")
    def base64_contents(self, root: FileRead, info: Info) -> str:
        filestorage = info.context["filestorage"]
        data = cast(
            bytes, filestorage.load_file(root.file_store, root.file_name, binary=True)
        )
        data = b64encode(data)
        return data.decode("ascii")


# Organisation Unit Refresh
# -------------------------
@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRefreshRead,
    all_fields=True,
    description="Response model for Organisation Unit refresh event.",
)
class OrganisationUnitRefresh:
    pass


# Configuration
# -------------
def get_settings_value(key: str) -> Any:
    """Get the settings value.

    Args:
        key: The settings key.

    Returns:
        The settings value.
    """
    return getattr(config.get_settings(), key)


@strawberry.experimental.pydantic.type(
    model=ConfigurationRead,
    all_fields=True,
    description="A configuration setting",
)
class Configuration:
    @strawberry.field(description="JSONified value")
    def jsonified_value(self, root: ConfigurationRead) -> str:
        """Get the jsonified value.

        Returns:
            The value.
        """
        return json.dumps(jsonable_encoder(get_settings_value(root.key)))

    @strawberry.field(description="Stringified value")
    def stringified_value(self, root: ConfigurationRead) -> str:
        """Get the stringified value.

        Returns:
            The value.
        """
        return str(get_settings_value(root.key))
