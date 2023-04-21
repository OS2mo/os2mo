# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph."""
import json
import re
from base64 import b64encode
from collections.abc import Awaitable
from collections.abc import Callable
from datetime import date
from datetime import datetime
from functools import partial
from inspect import Parameter
from inspect import signature
from itertools import chain
from typing import Annotated
from typing import Any
from typing import cast
from typing import Generic
from typing import TypeVar
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from more_itertools import only
from sqlalchemy import select
from starlette_context import context
from strawberry import UNSET
from strawberry.types import Info

from .health import health_map
from .models import ConfigurationRead
from .models import FileRead
from .models import HealthRead
from .models import OrganisationUnitRefreshRead
from .permissions import gen_read_permission
from .permissions import IsAuthenticatedPermission
from .resolver_map import resolver_map
from .resolvers import AddressResolver
from .resolvers import AssociationResolver
from .resolvers import ClassResolver
from .resolvers import EmployeeResolver
from .resolvers import EngagementAssociationResolver
from .resolvers import EngagementResolver
from .resolvers import FacetResolver
from .resolvers import get_date_interval
from .resolvers import ITSystemResolver
from .resolvers import ITUserResolver
from .resolvers import KLEResolver
from .resolvers import LeaveResolver
from .resolvers import ManagerResolver
from .resolvers import OrganisationUnitResolver
from .resolvers import RelatedUnitResolver
from .resolvers import RoleResolver
from .resolvers import StaticResolver
from .types import Cursor
from mora import common
from mora import config
from mora import lora
from mora.db import BrugerRegistrering
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRegistrering
from mora.service.address_handler import dar
from mora.service.address_handler import multifield_text
from mora.service.facet import is_class_uuid_primary
from mora.util import DEFAULT_TIMEZONE
from mora.util import parsedatetime
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
    resolver: Callable[..., Awaitable[R]],
    seeds: dict[str, Callable[[Any], Any]] | None = None,
    result_translation: Callable[[R], R] | None = None,
) -> Callable[..., Awaitable[R]]:
    """Seed the provided top-level resolver to be used in a field-level context.

    This function serves to create a new function which calls the `resolver` function
    with seeded values from the field-context in which it is called.

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
                OrganisationUnitResolver().resolve,
                {"parents": lambda root: [root.uuid]},
                lambda result: len(result.keys()),
            ),
            ...
        )
        ```
        In this example a `result_translation` lambda is also used to map from the list
        of OrganisationUnits returned by the resolver to the number of children found.

    Args:
        resolver: The top-level resolver function to seed arguments to.
        seeds:
            A dictionary mapping from parameter name to callables resolving the argument
            values from the root object.
        result_translation:
            A result translation callable translating the resolver return value
            from one type to another. Uses the identity function if not provided.

    Returns:
        A seeded resolver function that accepts the same parameters as the
        `resolver.resolve` function, except with the `seeds` keys removed as parameters,
        and a `root` parameter with the 'any' type added.
    """
    # If no seeds was provided, default to the empty dict
    seeds = seeds or {}
    # If no result_translation function was provided, default to the identity function
    result_translation = result_translation or identity

    async def seeded_resolver(*args: Any, root: Any, **kwargs: Any) -> R:
        # Resolve arguments from the root object
        assert seeds is not None
        for key, argument_callable in seeds.items():
            kwargs[key] = argument_callable(root)
        result = await resolver(*args, **kwargs)
        assert result_translation is not None
        return result_translation(result)

    sig = signature(resolver)
    parameters = sig.parameters.copy()
    # Remove the `seeds` parameters from the parameter list, as these will be resolved
    # from the root object on call-time instead.
    for key in seeds.keys():
        del parameters[key]
    # Add the `root` parameter to the parameter list, as it is required for all the
    # `seeds` resolvers to determine call-time parameters.
    parameter_list = list(parameters.values())
    parameter_list = [
        Parameter("root", Parameter.POSITIONAL_OR_KEYWORD, annotation=Any)
    ] + parameter_list
    # Generate and apply our new signature to the seeded_resolver function
    new_sig = sig.replace(parameters=parameter_list)
    seeded_resolver.__signature__ = new_sig  # type: ignore[attr-defined]

    return seeded_resolver


# seed_resolver functions pre-seeded with result_translation functions assuming that
# only a single UUID will be returned, converting the objects list to either a list or
# an optional entity.
seed_resolver_list = partial(
    seed_resolver,
    result_translation=lambda result: list(chain.from_iterable(result.values())),
)
seed_resolver_only = partial(
    seed_resolver,
    result_translation=lambda result: only(chain.from_iterable(result.values())),
)
# TODO: Eliminate optional list
seed_resolver_only_list = partial(
    seed_resolver,
    result_translation=lambda result: list(chain.from_iterable(result.values()))
    or None,
)
seed_resolver_one = partial(
    seed_resolver,
    result_translation=lambda result: one(chain.from_iterable(result.values())),
)
seed_static_resolver_list = seed_resolver
seed_static_resolver_only = partial(
    seed_resolver,
    result_translation=only,
)
seed_static_resolver_one = partial(
    seed_resolver,
    result_translation=one,
)


def uuid2list(uuid: UUID | None) -> list[UUID]:
    """Convert an optional uuid to a list.

    Args:
        uuid: Optional uuid to wrap in a list.

    Return:
        Empty list if uuid was none, single element list containing the uuid otherwise.
    """
    if uuid is None:
        return []
    return [uuid]


def model2dbregistration(model: Any) -> Any:
    mapping = {
        ClassRead: KlasseRegistrering,
        EmployeeRead: BrugerRegistrering,
        FacetRead: FacetRegistrering,
        OrganisationUnitRead: OrganisationEnhedRegistrering,
        AddressRead: OrganisationFunktionRegistrering,
        AssociationRead: OrganisationFunktionRegistrering,
        EngagementAssociationRead: OrganisationFunktionRegistrering,
        EngagementRead: OrganisationFunktionRegistrering,
        ITSystemRead: ITSystemRegistrering,
        ITUserRead: OrganisationFunktionRegistrering,
        KLERead: KlasseRegistrering,
        LeaveRead: OrganisationFunktionRegistrering,
        RoleRead: OrganisationFunktionRegistrering,
        ManagerRead: OrganisationFunktionRegistrering,
    }
    return mapping[model]


@strawberry.type
class Registration:
    registration_id: int
    # TODO: Let datetimes be lazily resolved
    start: datetime
    end: datetime | None
    # UUID of who made the change
    actor: UUID


@strawberry.type
class Response(Generic[MOObject]):
    uuid: UUID

    # Object cache is a temporary workaround ensuring that current resolvers keep
    # working as-is while also allowing for lazy resolution based entirely on the UUID.
    object_cache: strawberry.Private[list[MOObject]] = UNSET

    # Due to a limitation in Pythons typing support, it does not seem possible to fetch
    # the concrete class of generics from the generic definition, thus it must be
    # provided explicitly.
    model: strawberry.Private[type[MOObject]]

    @strawberry.field(
        description="Current state at query validity time",
        permission_classes=[IsAuthenticatedPermission],
    )
    async def current(self, root: "Response", info: Info) -> MOObject | None:
        def active_now(obj: Any) -> bool:
            """Predicate on whether the object is active right now.

            Args:
                obj: The object to test.

            Returns:
                True if the object is active right now, False otherwise.
            """
            now = datetime.now().replace(tzinfo=DEFAULT_TIMEZONE)
            datetime_min = datetime.min.replace(tzinfo=DEFAULT_TIMEZONE)
            datetime_max = datetime.max.replace(tzinfo=DEFAULT_TIMEZONE)
            return (
                (obj.validity.from_date or datetime_min)
                < now
                < (obj.validity.to_date or datetime_max)
            )

        # TODO: This should really do its own instantaneous query to find whatever is
        #       active right now, regardless of the values in objects.
        objects = await Response.objects(self, root, info)
        return only(filter(active_now, objects))

    @strawberry.field(
        description="Validities at query registration time",
        permission_classes=[IsAuthenticatedPermission],
    )
    async def objects(self, root: "Response", info: Info) -> list[MOObject]:
        # If the object_cache is filled our request has already been resolved elsewhere
        if root.object_cache != UNSET:
            return root.object_cache
        # If the object cache has not been filled we must resolve objects using the uuid
        resolver = resolver_map[root.model]["loader"]
        return await info.context[resolver].load(root.uuid)

    # TODO: Implement using a dataloader
    @strawberry.field(
        description="Registrations for the current entity",
        permission_classes=[IsAuthenticatedPermission],
    )
    async def registrations(
        self,
        root: "Response",
        info: Info,
        actors: list[UUID] | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Registration]:
        table = model2dbregistration(root.model)
        dates = get_date_interval(start, end)
        query = select(table).where(
            table.uuid == root.uuid,
            table.registreringstid_start.between(
                dates.from_date or datetime(1, 1, 1),
                dates.to_date or datetime(9999, 12, 31),
            ),
            table.registreringstid_slut.between(
                dates.from_date or datetime(1, 1, 1),
                dates.to_date or datetime(9999, 12, 31),
            ),
        )
        if actors is not None:
            query = query.where(table.actor.in_(actors))

        def row2registration(res: Any) -> Registration:
            start: datetime = parsedatetime(res.registreringstid_start)
            end: datetime | None = parsedatetime(res.registreringstid_slut)
            assert end is not None
            if end.date() == date(9999, 12, 31):
                end = None

            return Registration(  # type: ignore
                registration_id=res.id,
                start=start,
                end=end,
                actor=res.actor,
            )

        session = info.context["sessionmaker"]()
        async with session.begin():
            result = await session.scalars(query)
            result = list(map(row2registration, result))
            return result


LazySchema = strawberry.lazy(".schema")

LazyAddress = Annotated["Address", LazySchema]
LazyAssociation = Annotated["Association", LazySchema]
LazyClass = Annotated["Class", LazySchema]
LazyEmployee = Annotated["Employee", LazySchema]
LazyEngagement = Annotated["Engagement", LazySchema]
LazyEngagementAssociation = Annotated["EngagementAssociation", LazySchema]
LazyFacet = Annotated["Facet", LazySchema]
LazyITSystem = Annotated["ITSystem", LazySchema]
LazyITUser = Annotated["ITUser", LazySchema]
LazyKLE = Annotated["KLE", LazySchema]
LazyLeave = Annotated["Leave", LazySchema]
LazyManager = Annotated["Manager", LazySchema]
LazyOrganisationUnit = Annotated["OrganisationUnit", LazySchema]
LazyRelatedUnit = Annotated["RelatedUnit", LazySchema]
LazyRole = Annotated["Role", LazySchema]

# Address
# -------


@strawberry.experimental.pydantic.type(
    model=AddressRead,
    all_fields=True,
    description="Address information for an employee or organisation unit",
)
class Address:
    address_type: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve, {"uuids": lambda root: [root.address_type_uuid]}
        ),
        description="Address type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    visibility: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.visibility_uuid)}
        ),
        description="Address visibility",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Connected employee. "
        "Note that this is mutually exclusive with the org_unit field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
        ),
        description="Connected organisation unit. "
        "Note that this is mutually exclusive with the employee field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            EngagementResolver().resolve,
            {"uuids": lambda root: uuid2list(root.engagement_uuid)},
        ),
        description="Connected Engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    @strawberry.field(description="Name of address")
    async def name(self, root: AddressRead, info: Info) -> str | None:
        address_type = await Address.address_type(root=root, info=info)  # type: ignore[operator]

        if address_type.scope == "MULTIFIELD_TEXT":
            return multifield_text.name(root.value, root.value2)

        if address_type.scope == "DAR":
            dar_loader = context["dar_loader"]
            address_object = await dar_loader.load(UUID(root.value))
            return dar.name_from_dar_object(address_object)

        return root.value

    @strawberry.field(description="href of address")
    async def href(self, root: AddressRead, info: Info) -> str | None:
        address_type = await Address.address_type(root=root, info=info)  # type: ignore[operator]

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


# Association
# -----------


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    all_fields=True,
    description="Connects organisation units and employees",
)
class Association:
    association_type: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve,
            {"uuids": lambda root: uuid2list(root.association_type_uuid)},
        ),
        description="Association type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    dynamic_class: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.dynamic_class_uuid)}
        ),
        description="dynamic class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.primary_uuid)}
        ),
        description="Primary status",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make optional employee
    substitute: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.substitute_uuid)}
        ),
        description="Connected substitute employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    job_function: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.job_function_uuid)}
        ),
        description="Connected job function",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Can there be more than one ITUser per association?
    it_user: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver().resolve, {"uuids": lambda root: uuid2list(root.it_user_uuid)}
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
    parent: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.parent_uuid)}
        ),
        description="Immediate parent class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    children: list[LazyClass] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver().resolve,
            {"parents": lambda root: [root.uuid]},
        ),
        description="Immediate descendants of the class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    facet: LazyFacet = strawberry.field(
        resolver=seed_static_resolver_one(
            FacetResolver().resolve, {"uuids": lambda root: [root.facet_uuid]}
        ),
        description="Associated facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    @strawberry.field(
        description="Associated top-level facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )
    async def top_level_facet(self, root: ClassRead, info: Info) -> "Facet":
        if root.parent_uuid is None:
            return await Class.facet(root=root, info=info)  # type: ignore[operator]
        parent_node = await Class.parent(root=root, info=info)  # type: ignore[operator,misc]
        return await Class.top_level_facet(self=self, root=parent_node, info=info)

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

    engagements: list[LazyEngagement] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Engagements for the employee",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    manager_roles: list[LazyManager] = strawberry.field(
        resolver=seed_resolver_list(
            ManagerResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Manager roles for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=seed_resolver_list(
            AddressResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Addresses for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Leaves for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Associations for the employee",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    roles: list[LazyRole] = strawberry.field(
        resolver=seed_resolver_list(
            RoleResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="Roles for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver().resolve,
            {"employees": lambda root: [root.uuid]},
        ),
        description="IT users for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    engagement_associations: list[LazyEngagementAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver().resolve,
            {"employees": lambda root: [root.uuid]},
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
    engagement_type: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve,
            {"uuids": lambda root: [root.engagement_type_uuid]},
        ),
        description="Engagement type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    job_function: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve,
            {"uuids": lambda root: [root.job_function_uuid]},
        ),
        description="Job function",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.primary_uuid)}
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

    leave: LazyLeave | None = strawberry.field(
        resolver=seed_resolver_only(
            LeaveResolver().resolve, {"uuids": lambda root: uuid2list(root.leave_uuid)}
        ),
        description="Related leave",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
        ),
        description="Related organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement_associations: list[LazyEngagementAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver().resolve,
            {"engagements": lambda root: [root.uuid]},
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
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make concrete engagement
    engagement: list[LazyEngagement] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver().resolve,
            {"uuids": lambda root: [root.engagement_uuid]},
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement_association_type: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve,
            {"uuids": lambda root: [root.engagement_association_type_uuid]},
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
    classes: list[LazyClass] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver().resolve, {"facets": lambda root: [root.uuid]}
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
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            EngagementResolver().resolve,
            {"uuids": lambda root: uuid2list(root.engagement_uuid)},
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    itsystem: LazyITSystem = strawberry.field(
        resolver=seed_static_resolver_one(
            ITSystemResolver().resolve, {"uuids": lambda root: [root.itsystem_uuid]}
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
    kle_number: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve, {"uuids": lambda root: [root.kle_number_uuid]}
        ),
        description="KLE number",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    kle_aspects: list[LazyClass] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver().resolve,
            {"uuids": lambda root: root.kle_aspect_uuids or []},
        ),
        description="KLE Aspects",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
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
    leave_type: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve, {"uuids": lambda root: [root.leave_type_uuid]}
        ),
        description="Leave type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    engagement: LazyEngagement | None = strawberry.field(
        resolver=seed_resolver_only(
            EngagementResolver().resolve,
            {"uuids": lambda root: [root.engagement_uuid]},
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
    manager_type: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.manager_type_uuid)}
        ),
        description="Manager type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    manager_level: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.manager_level_uuid)}
        ),
        description="Manager level",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    responsibilities: list[LazyClass] = strawberry.field(
        resolver=seed_static_resolver_list(
            ClassResolver().resolve,
            {"parents": lambda root: root.responsibility_uuids or []},
        ),
        description="Manager responsibilities",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=seed_resolver_only_list(
            EmployeeResolver().resolve, {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Manager identity details",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: [root.org_unit_uuid]},
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
    parent: LazyOrganisationUnit | None = strawberry.field(
        resolver=seed_resolver_only(
            OrganisationUnitResolver().resolve,
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
        parent = await OrganisationUnit.parent(root=root, info=info)  # type: ignore
        if parent is None:
            return []
        ancestors = await OrganisationUnit.ancestors(self=self, root=parent, info=info)  # type: ignore
        return [parent] + ancestors

    children: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"parents": lambda root: [root.uuid]},
        ),
        description="The immediate descendants in the organisation tree",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    child_count: int = strawberry.field(
        resolver=seed_resolver(
            OrganisationUnitResolver().resolve,
            {"parents": lambda root: [root.uuid]},
            lambda result: len(result.keys()),
        ),
        description="Children count of the organisation unit.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    # TODO: Add _uuid suffix to RAModel and remove _model suffix here
    org_unit_hierarchy_model: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.org_unit_hierarchy)}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    unit_type: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.unit_type_uuid)}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    org_unit_level: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.org_unit_level_uuid)}
        ),
        description="Organisation unit level",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    time_planning: LazyClass | None = strawberry.field(
        resolver=seed_static_resolver_only(
            ClassResolver().resolve, {"uuids": lambda root: uuid2list(root.time_planning_uuid)}
        ),
        description="Time planning strategy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    engagements: list[LazyEngagement] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver().resolve,
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
        resolver = seed_resolver_list(ManagerResolver().resolve)
        result = await resolver(root=root, info=info, org_units=[root.uuid])
        if result:
            return result  # type: ignore
        if not inherit:
            return []
        parent = await OrganisationUnit.parent(root=root, info=info)  # type: ignore
        if parent is None:
            return []
        return await OrganisationUnit.managers(
            self=self, root=parent, info=info, inherit=True
        )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=seed_resolver_list(
            AddressResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related addresses",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related leaves",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    roles: list[LazyRole] = strawberry.field(
        resolver=seed_resolver_list(
            RoleResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related roles",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related IT users",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    kles: list[LazyKLE] = strawberry.field(
        resolver=seed_resolver_list(
            KLEResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="KLE responsibilites for the organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    related_units: list[LazyRelatedUnit] = strawberry.field(
        resolver=seed_resolver_list(
            RelatedUnitResolver().resolve,
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related units for the organisational unit",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("related_unit"),
        ],
    )

    engagement_associations: list[LazyEngagementAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver().resolve,
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
    org_units: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: root.org_unit_uuids or []},
        ),
        description="Related organisation units",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Role
# ----
@strawberry.experimental.pydantic.type(
    model=RoleRead,
    all_fields=True,
    description="Role an employee has within an organisation unit",
)
class Role:
    role_type: LazyClass = strawberry.field(
        resolver=seed_static_resolver_one(
            ClassResolver().resolve, {"uuids": lambda root: [root.role_type_uuid]}
        ),
        description="Role type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver().resolve, {"uuids": lambda root: [root.employee_uuid]}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver().resolve,
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


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
