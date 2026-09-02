# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry type for chosing validity."""

from collections.abc import Iterable
from collections.abc import Iterator
from datetime import datetime
from textwrap import dedent
from typing import Any
from typing import Generic
from typing import Protocol
from uuid import UUID

import strawberry
from more_itertools import only
from strawberry import UNSET
from strawberry.types.nodes import SelectedField

from mora.graphapi.context import MOInfo
from mora.graphapi.fields import Metadata
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import OwnerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead
from mora.graphapi.version import Version as GraphQLVersion
from mora.util import NEGATIVE_INFINITY
from mora.util import POSITIVE_INFINITY
from mora.util import now

from .graphql_utils import LoadKey
from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .moobject import MOObject
from .paged import to_objects
from .policies import POLICY_FOR
from .policies import Denied
from .policies import ObjectPermission
from .policies import PolicyError
from .policies import PolicyKey
from .registrationbase import Registration
from .registrationbase import RegistrationBase
from .resolver_map import get_dataloader
from .resolvers import registration_resolver
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
        OwnerRead: "owner",
        RelatedUnitRead: "related",
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
        "role": RoleBindingRead,
        "rolebinding": RoleBindingRead,
        "manager": ManagerRead,
        "owner": OwnerRead,
        "related": RelatedUnitRead,
    }
    return mapping[name]


class HasUUIDModel(Protocol):
    @property
    def uuid(self) -> UUID: ...

    @property
    def model(self) -> type[Any] | str: ...


def _collection(root: HasUUIDModel) -> str | None:
    """The policy-guarded collection *root* belongs to, if any.

    Collections without a policy are still gated by `RBAC_MAP`, and their
    content is never withheld here.
    """
    model = root.model
    name = model if isinstance(model, str) else model2name(model)
    return name if name in POLICY_FOR else None


def _selected(selections: Iterable[Any]) -> Iterator[str]:
    """The field names in *selections*, descending into fragments.

    A fragment is only a way of writing the selection down, so the fields
    inside one count as asked for; skipping them would let a policy be
    sidestepped by wrapping the selection in `... on Address`.
    """
    for selection in selections:
        if isinstance(selection, SelectedField):
            yield selection.name
        else:
            yield from _selected(selection.selections)


def _requested(info: MOInfo) -> frozenset[str]:
    """The fields asked for below the field being resolved."""
    return frozenset(
        name for field in info.selected_fields for name in _selected(field.selections)
    )


async def _permission(root: HasUUIDModel, info: MOInfo) -> ObjectPermission | None:
    """What the policies allow of *root*, or None if its collection has none.

    The lookup is batched across the objects of a page.
    """
    collection = _collection(root)
    if collection is None:
        return None
    return await info.context.dataloaders.policy_loader.load(
        PolicyKey(collection, root.uuid)
    )


async def _withheld(root: HasUUIDModel, info: MOInfo) -> frozenset[str]:
    """Which of the requested fields the policies withhold from *root*.

    Empty when the object may be read as asked, so the caller resolves it
    normally. Asked to error rather than withhold, this is where the caller
    finds out: it knows both what was touched and what may be read, so it
    can say which field it was.
    """
    permission = await _permission(root, info)
    if permission is None:
        return frozenset()
    withheld = permission.withheld(_requested(info))
    if withheld and getattr(root, "denied", Denied.REMOVE) is Denied.ERROR:
        raise PolicyError(
            f"not allowed to read {', '.join(sorted(withheld))} of {root.uuid}"
        )
    return withheld


async def current_resolver(
    root: HasUUIDModel,
    info: MOInfo,
    at: datetime | None = UNSET,
    registration_time: datetime | None = None,
) -> Any | None:
    # The policies decide what may be read of this object, however it was
    # reached. Withheld content is null rather than an error.
    if await _withheld(root, info):
        return None

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
    info: MOInfo,
    start: datetime | None = UNSET,
    end: datetime | None = UNSET,
    registration_time: datetime | None = None,
) -> list[Any]:
    # Withheld content is an empty list rather than an error; `redacted`
    # tells it apart from having no validities in the interval.
    if await _withheld(root, info):
        return []
    # Hack to ensure model is of the right type
    # TODO: Refactor model on Response to be a string
    model = root.model
    if isinstance(model, str):
        model = name2model(model)

    assert isinstance(model, type)
    dataloader = get_dataloader(info, model)
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
    )
    async def current(
        self,
        root: "ResponseRegistration",
        info: MOInfo,
        at: datetime | None = UNSET,
    ) -> MOObject | None:
        return await current_resolver(root, info, at, root.start)

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
    )
    async def validities(  # pragma: no cover
        self,
        root: "ResponseRegistration",
        info: MOInfo,
        start: datetime | None = UNSET,
        end: datetime | None = UNSET,
    ) -> list[MOObject]:
        return await validity_resolver(root, info, start, end, root.start)


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

    # Reference to the underlying model type
    model: strawberry.Private[type[MOObject]]

    # What the read asked to have done with withheld content. Objects reached
    # outside a collection read, such as through a relation, keep the default.
    denied: strawberry.Private[Denied] = Denied.REMOVE

    @strawberry.field(
        description=dedent(
            """\
            Whether the policies withhold this object's content.

            Without this, a withheld object cannot be told apart from an
            ordinary one: `current` is already null when nothing is active
            right now, and the temporal lists are already empty when nothing
            falls in the interval.

            The UUID is returned either way, so an object which disappears
            entirely really was deleted, rather than merely hidden.
            """
        )
    )
    async def redacted(self, root: "Response", info: MOInfo) -> bool:
        permission = await _permission(root, info)
        if permission is None:
            return False
        return not permission.readable or bool(permission.denied_fields)

    @strawberry.field(
        description=dedent(
            """\
            Why this object's content is withheld, if it is.

            Names the policy-restricted fields which were denied, or is the
            bare statement that the object itself may not be read. Null when
            nothing is withheld.
            """
        )
    )
    async def reason(self, root: "Response", info: MOInfo) -> str | None:
        permission = await _permission(root, info)
        if permission is None:
            return None
        if not permission.readable:
            return "not allowed to read the object"
        if permission.denied_fields:
            denied = ", ".join(sorted(permission.denied_fields))
            return f"not allowed to read: {denied}"
        return None

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
    )
    async def validities(
        self,
        root: "Response",
        info: MOInfo,
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
        resolver=to_objects(
            seed_resolver(
                registration_resolver,
                {
                    "uuids": lambda root: uuid2list(root.uuid),
                    "models": lambda root: [model2name(root.model)],
                },
            )
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
        resolver=to_objects(
            seed_resolver(
                registration_resolver,
                {
                    "uuids": lambda root: uuid2list(root.uuid),
                    "models": lambda root: [model2name(root.model)],
                },
            )
        ),
        metadata=Metadata(version=lambda v: v >= GraphQLVersion.VERSION_27),
    )
