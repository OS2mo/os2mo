# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry type for chosing validity."""

from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import get_args
from uuid import UUID

import strawberry
from more_itertools import only
from strawberry import UNSET
from strawberry.types import Info

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.util import NEGATIVE_INFINITY
from mora.util import POSITIVE_INFINITY
from mora.util import now

from .graphql_utils import LoadKey
from .graphql_utils import uuid2list
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .permissions import IsAuthenticatedPermission
from .registration_resolver import registration_resolver
from .resolver_map import resolver_map
from .seed_resolver import seed_resolver

LazyRegistration = Annotated["Registration", strawberry.lazy(".registration")]  # type: ignore  # noqa: F821
MOObject = TypeVar("MOObject")
R = TypeVar("R")


def model2name(model: Any) -> Any:
    mapping = {
        ClassRead: "class",
        EmployeeRead: "employee",
        FacetRead: "facet",
        OrganisationUnitRead: "org_unit",
        AddressRead: "address",
        AssociationRead: "association",
        EngagementRead: "engagement",
        ITSystemRead: "itsystem",
        ITUserRead: "ituser",
        KLERead: "kle",
        LeaveRead: "leave",
        RoleBindingRead: "rolebinding",
        ManagerRead: "manager",
    }
    return mapping[model]


@strawberry.type(
    description=dedent(
        """\
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

    @strawberry.field(
        description=dedent(
            """\
            Actual / current state entrypoint.

            Returns the state of the object at current validity and current assertion time.

            A single object is returned as only one validity can be active at a given assertion time.

            Note:
            This the entrypoint is appropriate to use for actual-state integrations and UIs.
            """
        ),
        permission_classes=[IsAuthenticatedPermission],
    )
    async def current(
        self, root: "Response", info: Info, at: datetime | None = UNSET
    ) -> MOObject | None:
        def active_now(obj: Any) -> bool:
            """Predicate on whether the object is active right now.

            Args:
                obj: The object to test.

            Returns:
                True if the object is active right now, False otherwise.
            """
            if not hasattr(obj, "validity"):  # pragma: no cover
                return True

            from_date = obj.validity.from_date or NEGATIVE_INFINITY
            to_date = obj.validity.to_date or POSITIVE_INFINITY

            # TODO: This should just be a normal datetime compare, but due to legacy systems,
            #       ex dipex, we must use .date() to compare dates instead of datetimes.
            #       Remove when legacy systems handle datetimes properly.
            return from_date.date() <= now().date() <= to_date.date()

        def activity_tuple(obj: Any) -> datetime:
            if not hasattr(obj, "validity"):  # pragma: no cover
                return NEGATIVE_INFINITY
            if obj.validity.to_date is None:
                return POSITIVE_INFINITY
            return obj.validity.to_date

        if at:
            objects = await Response.validities(self, root, info, at, UNSET)
            return only(objects)

        # TODO: This should really do its own instantaneous query to find whatever is
        #       active right now, regardless of the values in objects.
        objects = await Response.validities(self, root, info)
        objects_active_now = filter(active_now, objects)

        # HACK: Due to legacy systems, ex dipex, we must use .date() to compare dates instead of datetimes.
        #       because of this, if we update entities on the same date shortly after each other,
        #       we may end up with multiple entities which are "active now", where only one is expected.
        #       To handle this, we first try to find an entity which is active now and has no end date.
        #       If we cannot find such an entity, we find the entity with largest to_date
        return max(objects_active_now, key=activity_tuple, default=None)

    @strawberry.field(
        description=dedent(
            """\
            Temporal state entrypoint.

            Returns the state of the object at varying validities and current assertion time.

            A list of objects are returned as only many different validity intervals can be active at a given assertion time.

            Note:
            This the entrypoint should be used for temporal integrations and UIs.
            For actual-state integrations, please consider using `current` instead.
            """
        ),
        permission_classes=[IsAuthenticatedPermission],
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            Use validities instead.
            """
        ),
    )
    async def objects(
        self,
        root: "Response",
        info: Info,
        start: datetime | None = UNSET,
        end: datetime | None = UNSET,
    ) -> list[MOObject]:
        objects = await Response.validities(self, root, info, start, end)
        return objects

    @strawberry.field(
        description=dedent(
            """\
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
    async def validities(
        self,
        root: "Response",
        info: Info,
        start: datetime | None = UNSET,
        end: datetime | None = UNSET,
    ) -> list[MOObject]:
        if start is UNSET and end is UNSET and root.object_cache != UNSET:
            return root.object_cache
        # If the object cache has not been filled we must resolve objects using the uuid
        resolver = resolver_map[response2model(root)]["loader"]
        dataloader = info.context[resolver]
        return await dataloader.load(LoadKey(root.uuid, start, end))

    # TODO: Implement using a dataloader
    registrations: list[LazyRegistration] = strawberry.field(
        description=dedent(
            """\
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
        resolver=seed_resolver(
            registration_resolver,
            {
                "uuids": lambda root: uuid2list(root.uuid),
                "models": lambda root: [model2name(response2model(root))],
            },
        ),
    )


ResolverResult = dict[UUID, list[MOObject]]
ResolverFunction = Callable[..., Awaitable[ResolverResult]]


def result_translation(
    mapper: Callable[[ResolverResult], R],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[R]]]:
    def wrapper(
        resolver_func: ResolverFunction,
    ) -> Callable[..., Awaitable[R]]:
        @wraps(resolver_func)
        async def mapped_resolver(*args: Any, **kwargs: Any) -> Any:
            result = await resolver_func(*args, **kwargs)
            return mapper(result)

        return mapped_resolver

    return wrapper


def to_response_list(
    model: type[MOObject],
) -> Callable[[ResolverFunction], Callable[..., Awaitable[list[Response[MOObject]]]]]:
    def result2response_list(result: ResolverResult) -> list[Response[MOObject]]:
        # The type checker really does not like the below code.
        #
        # Mypy says: 'error: Variable "model" is not valid as a type', however every
        # attept to appease mypy by fixing the typing has ended up making the code
        # non-functional on runtime.
        #
        # Additionally it complains about construction of the Response object being
        # illegal as it 'Expected no arguments to "Response" constructor', however
        # attempting to resolve this using Pydantic's 'parse_obj_as' results in an
        # 'Fields of type \"<class 'Response'>\" are not supported."' error from
        # strawberry on runtime, whether implemented as:
        # '[parse_obj_as(T, x) for x in xs]' or 'parse_obj_as(list[T], xs)'.
        #
        # If you try to fix this typing issues here, please increment the following
        # counter as a warning to the next guy:
        #
        # total_hours_wasted_here = 4
        return [
            Response[model](uuid=uuid, object_cache=objects)  # type: ignore
            for uuid, objects in result.items()
        ]

    return result_translation(result2response_list)


def response2model(response: Response[MOObject]) -> MOObject:
    if not hasattr(response, "__orig_class__"):  # pragma: no cover
        raise ValueError(
            "Please ensure that `Response` is always instantiated with a type parameter, such as Response[Address](...) instead of Response(...)"
        )
    model = get_args(response.__orig_class__)[0]
    return model
