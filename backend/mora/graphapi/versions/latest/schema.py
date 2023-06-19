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
from functools import wraps
from inspect import Parameter
from inspect import signature
from itertools import chain
from textwrap import dedent
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
from .models import FileStore
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
from .resolvers import Resolver
from .resolvers import RoleResolver
from .types import Cursor
from .validity import OpenValidity
from .validity import Validity
from mora import common
from mora import config
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


# TODO: Remove RAModels dependency, be purely Strawberry models
# TODO: Deprecate all _uuid / _uuids relation fields in favor of relation objects


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


def raise_force_none_return_if_uuid_none(
    root: Any, get_uuid: Callable[[Any], UUID | None]
) -> list[UUID]:
    """Raise ForceNoneReturnError if uuid is None, a list with the uuid otherwise.

    Args:
        root: The root object from which the UUID will be extracted.
        get_uuid: Extractor function used to extract a UUID from root.

    Raises:
        ForceNonReturnError: If the extracted uuid is None.

    Returns:
        A list containing the UUID if the extracted uuid is not None.
    """
    uuid = get_uuid(root)
    if uuid is None:
        raise ForceNoneReturnError
    return uuid2list(uuid)


class ForceNoneReturnError(Exception):
    """Error to be raised to forcefully return None from decorated function.

    Note: The function that should forcefully return None must be decorated with
          `force_none_return_wrapper`.
    """

    pass


def force_none_return_wrapper(func: Callable) -> Callable:
    """Decorate a function to react to ForceNonReturnError.

    Args:
        func: The function to be decorated.

    Returns:
        A decorated function that returns None whenever ForceNonReturnError is raised.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> R | None:
        try:
            return await func(*args, **kwargs)
        except ForceNoneReturnError:
            return None

    return wrapper


def seed_resolver(
    resolver: Resolver,
    seeds: dict[str, Callable[[Any], Any]] | None = None,
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
seed_resolver_list: Callable[..., Any] = partial(
    seed_resolver,
    result_translation=lambda result: list(chain.from_iterable(result.values())),
)
seed_resolver_only: Callable[..., Any] = partial(
    seed_resolver,
    result_translation=lambda result: only(chain.from_iterable(result.values())),
)
seed_resolver_one: Callable[..., Any] = partial(
    seed_resolver,
    result_translation=lambda result: one(chain.from_iterable(result.values())),
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


@strawberry.type(
    description=dedent(
        """
    Bitemporal container.

    Mostly useful for auditing purposes seeing when data-changes were made and by whom.

    Note:
    Will eventually contain a full temporal axis per bitemporal container.
    """
    )
)
class Registration(Generic[MOObject]):
    registration_id: int = strawberry.field(
        description=dedent(
            """
        Internal registration ID for the registration.
        """
        ),
        deprecation_reason=dedent(
            """
            May be removed in the future once the bitemporal scheme is finished.
            """
        ),
    )

    start: datetime = strawberry.field(
        description=dedent(
            """
        Start of the bitemporal interval.
        """
        )
    )
    end: datetime | None = strawberry.field(
        description=dedent(
            """
        End of the bitemporal interval.

        `null` indicates the open interval, aka. infinity.
        """
        )
    )

    actor: UUID = strawberry.field(
        description=dedent(
            """
        UUID of the actor (integration or user) who changed the data.

        Note:
        Currently mostly returns `"42c432e8-9c4a-11e6-9f62-873cf34a735f"`.
        Will eventually contain for the UUID of the integration or user who mutated data, based on the JWT token.
        """
        )
    )


@strawberry.type(
    description=dedent(
        """
    Top-level container for (bi)-temporal and actual state data access.

    Contains a UUID uniquely denoting the bitemporal object.

    Contains three different object temporality axis:

    | entrypoint      | temporal axis | validity time | assertion time |
    |-----------------|---------------|---------------|----------------|
    | `current`       | actual state  | current       | current        |
    | `objects`       | temporal      | varying       | current        |
    | `registrations` | bitemporal    | varying       | varying        |

    The argument for having three different entrypoints into the data is limiting complexity according to use-case.

    That is, if a certain integration or UI only needs, say, actual state data, the complexities of the bitemporal data modelling is unwanted complexity, and as such, better left out.
    """
    )
)
class Response(Generic[MOObject]):
    uuid: UUID = strawberry.field(description="UUID of the bitemporal object")

    # Object cache is a temporary workaround ensuring that current resolvers keep
    # working as-is while also allowing for lazy resolution based entirely on the UUID.
    object_cache: strawberry.Private[list[MOObject]] = UNSET

    # Due to a limitation in Pythons typing support, it does not seem possible to fetch
    # the concrete class of generics from the generic definition, thus it must be
    # provided explicitly.
    model: strawberry.Private[type[MOObject]]

    @strawberry.field(
        description=dedent(
            """
            Actual / current state entrypoint.

            Returns the state of the object at current validity and current assertion time.

            A single object is returned as only one validity can be active at a given assertion time.

            Note:
            This the entrypoint is appropriate to use for actual-state integrations and UIs.
            """
        ),
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
            try:
                return (
                    (obj.validity.from_date or datetime_min)
                    < now
                    < (obj.validity.to_date or datetime_max)
                )
            except AttributeError:  # occurs when objects do not contain validity
                # TODO: Get rid of this entire branch by implementing non-static facet, etc.
                return True

        # TODO: This should really do its own instantaneous query to find whatever is
        #       active right now, regardless of the values in objects.
        objects = await Response.objects(self, root, info)
        return only(filter(active_now, objects))

    @strawberry.field(
        description=dedent(
            """
            Temporal state entrypoint.

            Returns the state of the object at varying validities and current assertion time.

            A list of objects are returned as only many different validity intervals can be active at a given assertion time.

            Note:
            This the entrypoint should be used for temporal integrations and UIs.
            For actual-state integrations, please consider using `current` instead.
            """
        ),
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
        description=dedent(
            """
            Bitemporal state entrypoint.

            Returns the state of the object at varying validities and varying assertion times.

            A list of bitemporal container objects are returned, each containing many different validity intervals.

            Note:
            This the entrypoint should only be used for bitemporal integrations and UIs, such as for auditing purposes.
            For temporal integration, please consider using `objects` instead.
            For actual-state integrations, please consider using `current` instead.

            **Warning**:
            This entrypoint should **not** be used to implement event-driven integrations.
            Such integration should rather utilize the AMQP-based event-system.
            """
        ),
        permission_classes=[IsAuthenticatedPermission],
    )
    # TODO: Document the arguments in the resolver once !1667 has been merged.
    async def registrations(
        self,
        root: "Response",
        info: Info,
        actors: list[UUID] | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Registration[MOObject]]:
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
    description="Address information for either an employee or organisational unit",
)
class Address:
    address_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: [root.address_type_uuid]}
        ),
        description=dedent(
            """
            Describes which type of address we're dealing with.

            Examples of user_keys:
            * `EmailUnit`
            * `p-nummer`
            * `PhoneEmployee`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    visibility: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.visibility_uuid)}
        ),
        description=dedent(
            """
            Describes who the address is visible to.

            Examples of user_keys:
            * `External` (Exposed to the internet)
            * `Internal` (Exposed to internal intranet)
            * `Secret` (Will stay in MO and not be exposed anywhere else)
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                EmployeeResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.employee_uuid,
                    )
                },
            ),
        ),
        description="Connected employee. "
        "Note that this is mutually exclusive with the org_unit field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                OrganisationUnitResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.org_unit_uuid,
                    )
                },
            ),
        ),
        description="Connected organisation unit. "
        "Note that this is mutually exclusive with the employee field",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                EngagementResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.engagement_uuid,
                    )
                },
            )
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

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    type_: str = strawberry.auto

    address_type_uuid: UUID = strawberry.auto

    employee_uuid: UUID | None = strawberry.auto

    org_unit_uuid: UUID | None = strawberry.auto

    engagement_uuid: UUID | None = strawberry.auto

    visibility_uuid: UUID | None = strawberry.auto

    value: str = strawberry.auto

    value2: str | None = strawberry.auto

    validity: Validity = strawberry.auto


# Association
# -----------


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    description="Connects organisation units and employees",
)
class Association:
    association_type: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(),
            {"uuids": lambda root: uuid2list(root.association_type_uuid)},
        ),
        description=dedent(
            """
            Describes the employee's connection to an organisation unit

            Examples:
            * `"Chairman"`
            * `"Leader"`
            * `"Employee"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    dynamic_class: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.dynamic_class_uuid)}
        ),
        # TODO: Document this
        # https://git.magenta.dk/rammearkitektur/os2mo/-/merge_requests/1694#note_216859
        description="dynamic classes",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.primary_uuid)}
        ),
        description=dedent(
            """
            Describes whether this is the primary association of the employee.

            Can be set to either of the primary-classes, by their UUID.

            Examples:
            * `primary(UUID)`
            * `non-primary(UUID)`
            * `explicitly-primary(UUID)`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(), {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make optional employee
    substitute: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(), {"uuids": lambda root: uuid2list(root.substitute_uuid)}
        ),
        description="Connected substitute employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    job_function: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.job_function_uuid)}
        ),
        description=dedent(
            """
            The position held by the employee

            Examples of user-keys:
            * `"Payroll consultant"`
            * `"Office student"`
            * `"Jurist"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Can there be more than one ITUser per association?
    it_user: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(), {"uuids": lambda root: uuid2list(root.it_user_uuid)}
        ),
        description="Connected IT user",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `association`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: AssociationRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    validity: Validity = strawberry.auto

    dynamic_class_uuid: UUID | None = strawberry.auto

    org_unit_uuid: UUID = strawberry.auto

    employee_uuid: UUID | None = strawberry.auto

    association_type_uuid: UUID | None = strawberry.auto

    primary_uuid: UUID | None = strawberry.auto

    substitute_uuid: UUID | None = strawberry.auto

    job_function_uuid: UUID | None = strawberry.auto

    it_user_uuid: UUID | None = strawberry.auto


# Class
# -----


@strawberry.experimental.pydantic.type(
    model=ClassRead,
    description="The value component of the class/facet choice setup",
)
class Class:
    parent: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.parent_uuid)}
        ),
        description="Immediate parent class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    children: list[LazyClass] = strawberry.field(
        resolver=seed_resolver_list(
            ClassResolver(),
            {"parents": lambda root: [root.uuid]},
        ),
        description="Immediate descendants of the class",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    facet: LazyFacet = strawberry.field(
        resolver=seed_resolver_one(
            FacetResolver(), {"uuids": lambda root: [root.facet_uuid]}
        ),
        description="Associated facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )

    @strawberry.field(
        description="Associated top-level facet",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("facet")],
    )
    async def top_level_facet(self, root: ClassRead, info: Info) -> LazyFacet:
        if root.parent_uuid is None:
            return await Class.facet(root=root, info=info)  # type: ignore[operator]
        parent_node = await Class.parent(root=root, info=info)  # type: ignore[operator,misc]
        return await Class.top_level_facet(self=self, root=parent_node, info=info)

    @strawberry.field(description="Full name, for backwards compatibility")
    async def full_name(self, root: ClassRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `class`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ClassRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    name: str = strawberry.auto

    facet_uuid: UUID = strawberry.auto

    org_uuid: UUID = strawberry.auto

    scope: str | None = strawberry.auto

    published: str | None = strawberry.auto

    parent_uuid: UUID | None = strawberry.auto

    example: str | None = strawberry.auto

    owner: UUID | None = strawberry.auto


# Employee
# --------


@strawberry.experimental.pydantic.type(
    model=EmployeeRead,
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
            EngagementResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="List of Engagements for the employee",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    manager_roles: list[LazyManager] = strawberry.field(
        resolver=seed_resolver_list(
            ManagerResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description=dedent(
            """List of UUIDS to connected manager roles to the Employee, empty if
            employee is not a manager
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=seed_resolver_list(
            AddressResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="Addresses for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="Leaves for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver(),
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
            RoleResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="Roles for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="IT users for the employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    engagement_associations: list[LazyEngagementAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver(),
            {"employees": lambda root: [root.uuid]},
        ),
        description="Engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `employee`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: EmployeeRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    cpr_no: str | None = strawberry.auto

    seniority: date | None = strawberry.auto

    givenname: str = strawberry.auto

    surname: str = strawberry.auto

    nickname_givenname: str | None = strawberry.auto

    nickname_surname: str | None = strawberry.auto

    validity: OpenValidity = strawberry.auto


# Engagement
# ----------


@strawberry.experimental.pydantic.type(
    model=EngagementRead,
    description="Employee engagement in an organisation unit",
)
class Engagement:
    engagement_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(),
            {"uuids": lambda root: [root.engagement_type_uuid]},
        ),
        description=dedent(
            """
            Describes the employee's affiliation to an organisation unit

            Examples:
            * `"Employed"`
            * `"Social worker"`
            * `"Employee (hourly wage)"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    job_function: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(),
            {"uuids": lambda root: [root.job_function_uuid]},
        ),
        description=dedent(
            """
            Describes the position of the employee in the organisation unit

            Examples:
            * `"Payroll consultant"`
            * `"Office student"`
            * `"Jurist"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.primary_uuid)}
        ),
        description=dedent(
            """
            Describes whether this is the primary association of the employee.

            Can be set to either of the primary-classes, by their UUID.

            Examples:
            * `primary(UUID)`
            * `non-primary(UUID)`
            * `explicitly-primary(UUID)`
            """
        ),
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
            LeaveResolver(), {"uuids": lambda root: uuid2list(root.leave_uuid)}
        ),
        description="Related leave",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(), {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
        ),
        description="Related organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement_associations: list[LazyEngagementAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementAssociationResolver(),
            {"engagements": lambda root: [root.uuid]},
        ),
        description="Engagement associations",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement_association"),
        ],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `engagement`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: EngagementRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    org_unit_uuid: UUID = strawberry.auto

    employee_uuid: UUID = strawberry.auto

    engagement_type_uuid: UUID = strawberry.auto

    job_function_uuid: UUID = strawberry.auto

    leave_uuid: UUID | None = strawberry.auto

    primary_uuid: UUID | None = strawberry.auto

    validity: Validity = strawberry.auto

    fraction: int | None = strawberry.auto

    extension_1: str | None = strawberry.auto

    extension_2: str | None = strawberry.auto

    extension_3: str | None = strawberry.auto

    extension_4: str | None = strawberry.auto

    extension_5: str | None = strawberry.auto

    extension_6: str | None = strawberry.auto

    extension_7: str | None = strawberry.auto

    extension_8: str | None = strawberry.auto

    extension_9: str | None = strawberry.auto

    extension_10: str | None = strawberry.auto


# Engagement Association
# ----------


@strawberry.experimental.pydantic.type(
    model=EngagementAssociationRead,
    description="Employee engagement in an organisation unit",
)
class EngagementAssociation:
    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove list, make concrete engagement
    engagement: list[LazyEngagement] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver(),
            {"uuids": lambda root: [root.engagement_uuid]},
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement_association_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(),
            {"uuids": lambda root: [root.engagement_association_type_uuid]},
        ),
        description="Related engagement association type",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `engagement_association`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: EngagementAssociationRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    validity: Validity = strawberry.auto

    org_unit_uuid: UUID = strawberry.auto

    engagement_uuid: UUID = strawberry.auto

    engagement_association_type_uuid: UUID = strawberry.auto


# Facet
# -----


@strawberry.experimental.pydantic.type(
    model=FacetRead,
    description="The key component of the class/facet choice setup",
)
class Facet:
    classes: list[LazyClass] = strawberry.field(
        resolver=seed_resolver_list(
            ClassResolver(), {"facets": lambda root: [root.uuid]}
        ),
        description="Associated classes",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `facet`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: FacetRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    published: str | None = strawberry.auto

    org_uuid: UUID = strawberry.auto

    parent_uuid: UUID | None = strawberry.auto

    description: str = strawberry.auto


# IT
# --


@strawberry.experimental.pydantic.type(
    model=ITSystemRead,
    description="Systems that IT users are connected to",
)
class ITSystem:
    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `itsystem`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ITSystemRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    name: str = strawberry.auto

    user_key: str = strawberry.auto

    system_type: str | None = strawberry.auto


@strawberry.experimental.pydantic.type(
    model=ITUserRead,
    description="User information related to IT systems",
)
class ITUser:
    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                EmployeeResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.employee_uuid,
                    )
                },
            ),
        ),
        description="Connected employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                OrganisationUnitResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.org_unit_uuid,
                    )
                },
            ),
        ),
        description="Connected organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                EngagementResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.engagement_uuid,
                    )
                },
            ),
        ),
        description="Related engagement",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    itsystem: LazyITSystem = strawberry.field(
        resolver=seed_resolver_one(
            ITSystemResolver(), {"uuids": lambda root: [root.itsystem_uuid]}
        ),
        description="Connected itsystem",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `it`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ITUserRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    itsystem_uuid: UUID = strawberry.auto

    employee_uuid: UUID | None = strawberry.auto

    org_unit_uuid: UUID | None = strawberry.auto

    engagement_uuid: UUID | None = strawberry.auto

    primary_uuid: UUID | None = strawberry.auto

    validity: Validity = strawberry.auto


# KLE
# ---


@strawberry.experimental.pydantic.type(
    model=KLERead,
    description="Kommunernes Landsforenings Emnesystematik",
)
class KLE:
    kle_number: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: [root.kle_number_uuid]}
        ),
        description="KLE number",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    kle_aspects: list[LazyClass] = strawberry.field(
        resolver=seed_resolver_list(
            ClassResolver(),
            {"uuids": lambda root: root.kle_aspect_uuids or []},
        ),
        description="KLE Aspects",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                OrganisationUnitResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.org_unit_uuid,
                    )
                },
            ),
        ),
        description="Associated organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `kle`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: KLERead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    uuid: UUID = strawberry.auto

    user_key: str = strawberry.auto

    kle_number_uuid: UUID = strawberry.auto

    kle_aspect_uuids: list[UUID] = strawberry.auto

    org_unit_uuid: UUID | None = strawberry.auto

    validity: Validity = strawberry.auto


# Leave
# -----


@strawberry.experimental.pydantic.type(
    model=LeaveRead,
    all_fields=True,
    description="Leave (e.g. parental leave) for employees",
)
class Leave:
    leave_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: [root.leave_type_uuid]}
        ),
        description=dedent(
            """
            Describes which kind of leave (e.g parental leave)

            Examples:
            * `"Maternity leave"`
            * `"Parental leave"`
            * `"Leave to care for sick relative"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(), {"uuids": lambda root: uuid2list(root.employee_uuid)}
        ),
        description="Related employee",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    engagement: LazyEngagement | None = strawberry.field(
        resolver=seed_resolver_only(
            EngagementResolver(),
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
    manager_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.manager_type_uuid)}
        ),
        description=dedent(
            """
            Describes the title of the Manager

            Examples:
            * `"Director"`
            * `"Area manager"`
            * `"Center manager"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    manager_level: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.manager_level_uuid)}
        ),
        description=dedent(
            """
            Describes the hierarchy of managers

            Examples:
            * `"Level 1"`
            * `"Level 2"`
            * `"Level 3"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    responsibilities: list[LazyClass] = strawberry.field(
        resolver=seed_resolver_list(
            ClassResolver(),
            {"uuids": lambda root: root.responsibility_uuids or []},
        ),
        description=dedent(
            """
            Returns a list of area of responsibilities that the Manager is responsible for

            Examples:
            * `["Responsible for buildings and areas"]
            * `["Responsible for buildings and areas", "Staff: Sick leave"]
            * `[]`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove list, make optional employee
    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            seed_resolver_list(
                EmployeeResolver(),
                {
                    "uuids": partial(
                        raise_force_none_return_if_uuid_none,
                        get_uuid=lambda root: root.employee_uuid,
                    )
                },
            ),
        ),
        description="Employee fulfilling the managerial position",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="Organisation unit being managed",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Organisation
# ------------


MUNICIPALITY_CODE_PATTERN = re.compile(r"urn:dk:kommune:(\d+)")


@strawberry.type(description="Root organisation - one and only one of these can exist")
class Organisation:
    # TODO: Eliminate the OrganisationRead model from here. Use self instead.

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: OrganisationRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Examples:
            * `root`
            * `0751` (municipality code)
            * `3b866d97-0b1f-48e0-8078-686d96f430b3` (copied entity UUID)
            * `Kolding Kommune` (municipality name)
            * `Magenta ApS` (company name)
            """
        )
    )
    async def user_key(self, root: OrganisationRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            Name of the organisation.

            Examples:
            * `root`
            * `Kolding Kommune` (or similar municipality name)
            * `Magenta ApS` (or similar company name)
            """
        )
    )
    async def name(self, root: OrganisationRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `organisation`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: OrganisationRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(
        description=dedent(
            """
            The municipality code.

            In Denmark; a 3 digit number uniquely identifying a municipality.
            Generally used to map the Local administrative units (LAU) of the
            Nomenclature of Territorial Units for Statistics (NUTS) standard.

            A list of all danish municipality codes can be found here:
            * https://danmarksadresser.dk/adressedata/kodelister/kommunekodeliste

            Examples:
            * `null` (unset)
            * `101` (Copenhagen)
            * `461` (Odense)
            * `751` (Aarhus)
            """
        )
    )
    async def municipality_code(self, root: OrganisationRead) -> int | None:
        """Get the municipality code for the organisation unit (if any).

        Returns:
            The municipality code, if any is found.
        """
        org = await common.get_connector().organisation.get(root.uuid)
        if org is None:
            return None
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
            OrganisationUnitResolver(),
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
    ) -> list[LazyOrganisationUnit]:
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
            OrganisationUnitResolver(),
            {"parents": lambda root: [root.uuid]},
        ),
        description="The immediate descendants in the organisation tree",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    child_count: int = strawberry.field(
        resolver=cast(
            Callable[..., Any],
            seed_resolver(
                OrganisationUnitResolver(),
                {"parents": lambda root: [root.uuid]},
                lambda result: len(result.keys()),
            ),
        ),
        description="Children count of the organisation unit.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    # TODO: Add _uuid suffix to RAModel and remove _model suffix here
    org_unit_hierarchy_model: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.org_unit_hierarchy)}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    unit_type: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.unit_type_uuid)}
        ),
        description="Organisation unit hierarchy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    # TODO: Remove org prefix from RAModel and remove it here too
    org_unit_level: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.org_unit_level_uuid)}
        ),
        description="Organisation unit level",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    time_planning: LazyClass | None = strawberry.field(
        resolver=seed_resolver_only(
            ClassResolver(), {"uuids": lambda root: uuid2list(root.time_planning_uuid)}
        ),
        description="Time planning strategy",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    engagements: list[LazyEngagement] = strawberry.field(
        resolver=seed_resolver_list(
            EngagementResolver(),
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
        resolver = seed_resolver_list(ManagerResolver())
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
            AddressResolver(),
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related addresses",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=seed_resolver_list(
            LeaveResolver(),
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related leaves",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=seed_resolver_list(
            AssociationResolver(),
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
            RoleResolver(),
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related roles",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("role")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=seed_resolver_list(
            ITUserResolver(),
            {"org_units": lambda root: [root.uuid]},
        ),
        description="Related IT users",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    kles: list[LazyKLE] = strawberry.field(
        resolver=seed_resolver_list(
            KLEResolver(),
            {"org_units": lambda root: [root.uuid]},
        ),
        description="KLE responsibilites for the organisation unit",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("kle")],
    )

    related_units: list[LazyRelatedUnit] = strawberry.field(
        resolver=seed_resolver_list(
            RelatedUnitResolver(),
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
            EngagementAssociationResolver(),
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
    description="An organisation unit relation mapping",
)
class RelatedUnit:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: RelatedUnitRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
        User-key of the entity.

        Usually constructed from the user-keys of our organisation units at creation time.

        Examples:
        * `"Administrative <-> Payroll"`
        * `"IT-Support <-> IT-Support`
        * `"Majora School <-> Alias School"`
        """
        )
    )
    async def user_key(self, root: RelatedUnitRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `related_units`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: RelatedUnitRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    validity: Validity = strawberry.auto

    org_unit_uuids: list[UUID] = strawberry.auto
    org_units: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: root.org_unit_uuids or []},
        ),
        description=dedent(
            """
            Related organisation units.

            Examples of user-keys:
            * `["Administrative", "Payroll"]`
            * `["IT-Support", "IT-Support]`
            * `["Majora School", "Alias School"]`

            Note:
            The result list should always be of length 2, corresponding to the elements of the bijection.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Role
# ----
@strawberry.experimental.pydantic.type(
    model=RoleRead,
    description="The role a person has within an organisation unit",
)
class Role:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: RoleRead) -> UUID:
        return root.uuid

    user_key: str = strawberry.auto

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `role`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: RoleRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    validity: Validity = strawberry.auto

    role_type_uuid: UUID = strawberry.auto
    role_type: LazyClass = strawberry.field(
        resolver=seed_resolver_one(
            ClassResolver(), {"uuids": lambda root: [root.role_type_uuid]}
        ),
        description=dedent(
            """
            The role that is being fulfilled.

            Examples of user-keys:
            * `"Staff representative"`
            * `"Coordinator"`
            * `"Security personnel"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    employee_uuid: UUID = strawberry.auto
    # TODO: Remove list, make concrete employee
    employee: list[LazyEmployee] = strawberry.field(
        resolver=seed_resolver_list(
            EmployeeResolver(), {"uuids": lambda root: [root.employee_uuid]}
        ),
        description="The person fulfilling the role.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    org_unit_uuid: UUID = strawberry.auto
    # TODO: Remove list, make concrete org-unit
    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=seed_resolver_list(
            OrganisationUnitResolver(),
            {"uuids": lambda root: [root.org_unit_uuid]},
        ),
        description="The organisational unit in which the role is being fulfilled.",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )


# Version
# -------
@strawberry.type(description="MO and DIPEX versions")
class Version:
    @strawberry.field(
        description=dedent(
            """
            OS2mo Version.

            Contains a [semantic version](https://semver.org/) on released versions of OS2mo.
            Contains the string `HEAD` on development builds of OS2mo.

            Examples:
            * `HEAD`
            * `22.2.6`
            * `21.0.0`
            """
        )
    )
    async def mo_version(self) -> str | None:
        """Get the mo version.

        Returns:
            The version.
        """
        return config.get_settings().commit_tag

    @strawberry.field(
        description=dedent(
            """
            OS2mo commit hash.

            Contains a git hash on released versions of OS2mo.
            Contains the empty string on development builds of OS2mo.

            Examples:
            * `""`
            * `880bd2009baccbdf795a8cef3b5b32b42c91c51b`
            * `b29e45449a857cf78725eff10c5856075417ea51`
            """
        )
    )
    async def mo_hash(self) -> str | None:
        """Get the mo commit hash.

        Returns:
            The commit hash.
        """
        return config.get_settings().commit_sha

    @strawberry.field(
        description="LoRa version. Returns the exact same as `mo_version`.",
        deprecation_reason="MO and LoRa are shipped and versioned together",
    )
    async def lora_version(self) -> str | None:
        """Get the lora version.

        Returns:
            The version.
        """
        return config.get_settings().commit_tag

    @strawberry.field(
        description=dedent(
            """
            DIPEX version.

            Contains a [semantic version](https://semver.org/) if configured.
            Contains the `null` on development builds of OS2mo.

            Examples:
            * `null`
            * `4.34.1`
            * `4.28.0`
            """
        )
    )
    async def dipex_version(self) -> str | None:
        return config.get_settings().confdb_dipex_version__do_not_use


@strawberry.type(description="Status on whether a specific subsystem is working")
class Health:
    identifier: str = strawberry.field(
        description=dedent(
            """
        Healthcheck identifier.

        Examples:
        * `"dataset"`
        * `"dar"`
        * `"amqp"`
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """
        Healthcheck status.

        Returns:
        * `true` if the healthcheck passed
        * `false` if the healthcheck failed
        * `null` if the healthcheck is irrelevant (submodule not loaded, etc)

        Note:
        Querying the healthcheck status executes the underlying healthcheck directly.
        Excessively querying this endpoint may have performance implications.
        """
        )
    )
    async def status(self) -> bool | None:
        return await health_map[self.identifier]()


T = TypeVar("T")


@strawberry.type(
    description=dedent(
        """
    Container for page information.

    Contains the cursors necessary to fetch other pages.
    Contains information on when to stop iteration.
    """
    )
)
class PageInfo:
    next_cursor: Cursor | None = strawberry.field(
        description=dedent(
            """
            Cursor for the next page of results.

            Should be provided to the `cursor` argument to iterate forwards.
            """
        ),
        default=None,
    )


@strawberry.type(description="Result page in cursor-based pagination.")
class Paged(Generic[T]):
    objects: list[T] = strawberry.field(
        description=dedent(
            """
            List of results.

            The number of elements is defined by the `limit` argument.
            """
        )
    )
    page_info: PageInfo = strawberry.field(
        description=dedent(
            """
            Container for page information.

            Contains the cursors necessary to fetch other pages.
            Contains information on when to stop iteration.
            """
        )
    )


# File
# ----
@strawberry.type(description="A stored file available for download.")
class File:
    file_store: FileStore = strawberry.field(
        description=dedent(
            """
        The store the file is in.

        The FileStore type lists all possible enum values.
    """
        )
    )

    file_name: str = strawberry.field(
        description=dedent(
            """
        Name of the file.

        Examples:
        * `"report.odt"`
        * `"result.csv"`
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """
        The textual contents of the file.

        Examples:
        * A csv-file:
        ```
        Year,Model,Make
        1997,Ford,E350
        2000,Mercury,Cougar
        ...
        ```
        * A textual report:
        ```
        Status of this Memo

        This document specifies an Internet standards track
        ...
        ```

        Note:
        This should only be used for text files formats such as `.txt` or `.csv`.
        For binary formats please use `base64_contents` instead.
        """
        )
    )
    def text_contents(self, info: Info) -> str:
        filestorage = info.context["filestorage"]
        return cast(str, filestorage.load_file(self.file_store, self.file_name))

    @strawberry.field(
        description=dedent(
            """
        The base64 encoded contents of the file.

        Examples:
        * A text file:
        ```
        TW96aWxsYSBQdWJsaWMgTGljZW5zZSBWZXJzaW9uIDIuMAo
        ...
        ```
        * A binary file:
        ```
        f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAAoF5GAAAA
        ...
        ```

        Note:
        While this works for binary and text files alike, it may be preferable to use `text_contents` for text files.
        """
        )
    )
    def base64_contents(self, info: Info) -> str:
        filestorage = info.context["filestorage"]
        data = cast(
            bytes, filestorage.load_file(self.file_store, self.file_name, binary=True)
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
@strawberry.type(description="A configuration setting.")
class Configuration:
    def get_settings_value(self) -> Any:
        """Get the settings value.

        Args:
            key: The settings key.

        Returns:
            The settings value.
        """
        return getattr(config.get_settings(), self.key)

    key: str = strawberry.field(
        description=dedent(
            """
        The unique settings identifier.

        Examples:
        * `commit_tag`
        * `environment`
        * `confdb_show_roles`
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """
        JSONified settings value.

        Examples:
        * `"true"`
        * `"\\"\\""`
        * `"null"`
        * `"[]"`
        """
        )
    )
    def jsonified_value(self) -> str:
        """Get the jsonified value.

        Returns:
            The value.
        """
        return json.dumps(jsonable_encoder(self.get_settings_value()))

    @strawberry.field(
        description=dedent(
            """
        Stringified settings value.

        Examples:
        * `"True"`
        * `""`
        * `"None"`
        * `"[]"`
        """
        )
    )
    def stringified_value(self) -> str:
        """Get the stringified value.

        Returns:
            The value.
        """
        return str(self.get_settings_value())
