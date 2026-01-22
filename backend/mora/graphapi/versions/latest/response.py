# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry type for chosing validity."""

from datetime import datetime
from textwrap import dedent
from typing import Any
from typing import Generic
from typing import Protocol
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

from ...fields import Metadata
from ...version import Version as GraphQLVersion
from .graphql_utils import LoadKey
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .moobject import MOObject
from .permissions import IsAuthenticatedPermission
from .registration import Registration
from .registration import registration_resolver
from .registrationbase import RegistrationBase
from .resolver_map import resolver_map
from .seed_resolver import seed_resolver
from .utils import uuid2list


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


def name2model(name: str) -> Any:
    mapping = {
        "class": ClassRead,
        "employee": EmployeeRead,
        "facet": FacetRead,
        "org_unit": OrganisationUnitRead,
        "address": AddressRead,
        "association": AssociationRead,
        "engagement": EngagementRead,
        "itsystem": ITSystemRead,
        "ituser": ITUserRead,
        "kle": KLERead,
        "leave": LeaveRead,
        "rolebinding": RoleBindingRead,
        "manager": ManagerRead,
    }
    return mapping[name]


class HasUUIDModel(Protocol):
    @property
    def uuid(self) -> UUID: ...

    @property
    def model(self) -> type[Any] | str: ...


async def current_resolver(
    root: HasUUIDModel,
    info: Info,
    at: datetime | None = UNSET,
    registration_time: datetime | None = None,
) -> Any | None:
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

    if at or registration_time:
        objects = await validity_resolver(root, info, at, UNSET, registration_time)
        return only(objects)

    # TODO: This should really do its own instantaneous query to find whatever is
    #       active right now, regardless of the values in objects.
    objects = await validity_resolver(root, info)
    objects_active_now = filter(active_now, objects)

    # HACK: Due to legacy systems, ex dipex, we must use .date() to compare dates instead of datetimes.
    #       because of this, if we update entities on the same date shortly after each other,
    #       we may end up with multiple entities which are "active now", where only one is expected.
    #       To handle this, we first try to find an entity which is active now and has no end date.
    #       If we cannot find such an entity, we find the entity with largest to_date
    return max(objects_active_now, key=activity_tuple, default=None)


async def validity_resolver(
    root: HasUUIDModel,
    info: Info,
    start: datetime | None = UNSET,
    end: datetime | None = UNSET,
    registration_time: datetime | None = None,
) -> list[Any]:
    # Hack to ensure model is of the right type
    # TODO: Refactor model on Response to be a string
    model = root.model
    if isinstance(model, str):
        model = name2model(model)

    resolver = resolver_map[model]["loader"]
    dataloader = info.context[resolver]
    return await dataloader.load(LoadKey(root.uuid, start, end, registration_time))


@strawberry.type(
    description=dedent(
        """\
    Bitemporal container.

    Mostly useful for auditing purposes seeing when data-changes were made and by whom.

    Note:
    Will eventually contain a full temporal axis per bitemporal container.

    **Warning**:
    This entry should **not** be used to implement event-driven integrations.
    Such integration should rather utilize the GraphQL-based event-system.
    """
    )
)
class ResponseRegistration(RegistrationBase, Generic[MOObject]):
    pass


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

    # Reference to the underlying model type
    model: strawberry.Private[type[MOObject]]

    # NOTE: The `current` and `validities` field also occur on `ModelRegistration`.
    current: MOObject | None = strawberry.field(
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
        resolver=current_resolver,
    )

    objects: list[MOObject] = strawberry.field(
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
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            Use validities instead.
            """
        ),
        resolver=validity_resolver,
    )

    # NOTE: This field cannot be rewritten as the one above due to:
    # https://github.com/strawberry-graphql/strawberry/issues/4139
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
    async def validities(
        self,
        root: "Response",
        info: Info,
        start: datetime | None = UNSET,
        end: datetime | None = UNSET,
        registration_time: datetime | None = None,
    ) -> list[MOObject]:
        return await validity_resolver(root, info, start, end, registration_time)

    # TODO: Implement using a dataloader
    registrations__v26: list[Registration] = strawberry.field(
        name="registrations",
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
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        permission_classes=[IsAuthenticatedPermission],
        resolver=seed_resolver(
            registration_resolver,
            {
                "uuids": lambda root: uuid2list(root.uuid),
                "models": lambda root: [model2name(root.model)],
            },
        ),
        metadata=Metadata(version=lambda v: v <= GraphQLVersion.VERSION_26),
    )

    registrations__v27: list[ResponseRegistration[MOObject]] = strawberry.field(
        name="registrations",
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
            Such integration should rather utilize the GraphQL-based event-system.
            """
        ),
        permission_classes=[IsAuthenticatedPermission],
        resolver=seed_resolver(
            registration_resolver,
            {
                "uuids": lambda root: uuid2list(root.uuid),
                "models": lambda root: [model2name(root.model)],
            },
        ),
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_27),
    )
