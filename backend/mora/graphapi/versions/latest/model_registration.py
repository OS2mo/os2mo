# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from textwrap import dedent
from typing import Any
from typing import Generic
from typing import ParamSpec
from typing import TypeVar
from uuid import UUID

import strawberry
from strawberry import Info

from .actor import Actor
from .actor import actor_uuid_to_actor
from .moobject import MOObject
from .schema import KLE
from .schema import Address
from .schema import Association
from .schema import Class
from .schema import Employee
from .schema import Engagement
from .schema import Facet
from .schema import ITSystem
from .schema import ITUser
from .schema import Leave
from .schema import Manager
from .schema import OrganisationUnit
from .schema import Owner
from .schema import RelatedUnit
from .schema import RoleBinding

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


@strawberry.interface(
    description=dedent(
        """\
    Bitemporal container.

    Mostly useful for auditing purposes seeing when data-changes were made and by whom.

    Note:
    Will eventually contain a full temporal axis per bitemporal container.

    **Warning**:
    This entry should **not** be used to implement event-driven integrations.
    Such integration should rather utilize the AMQP-based event-system.
    """
    )
)
class IRegistration:
    registration_id: int = strawberry.field(
        description=dedent(
            """\
        Internal registration ID for the registration.
        """
        ),
        deprecation_reason=dedent(
            """\
            May be removed in the future once the bitemporal scheme is finished.
            """
        ),
    )

    start: datetime = strawberry.field(
        description=dedent(
            """\
        Start of the bitemporal interval.

        Examples:
        * `"1970-01-01T00:00:00.000000+00:00"`
        * `"2019-12-18T12:55:15.348614+00:00"`
        """
        )
    )
    end: datetime | None = strawberry.field(
        description=dedent(
            """\
        End of the bitemporal interval.

        `null` indicates the open interval, aka. infinity.

        Examples:
        * `"1970-01-01T00:00:00.000000+00:00"`
        * `"2019-12-18T12:55:15.348614+00:00"`
        * `null`
        """
        )
    )

    actor: UUID = strawberry.field(
        description=dedent(
            """\
        UUID of the actor (integration or user) who changed the data.

        Note:
        Currently mostly returns `"42c432e8-9c4a-11e6-9f62-873cf34a735f"`.
        Will eventually contain for the UUID of the integration or user who mutated data, based on the JWT token.
        """
        ),
        deprecation_reason="Use actor_object.",
    )

    @strawberry.field(
        description=dedent(
            """\
            Object for the actor (integration or user) who changed the data.
            """
        )
    )
    def actor_object(self, root: "IRegistration", info: Info) -> Actor:
        return actor_uuid_to_actor(root.actor)

    # Name of the entity model
    model: str = strawberry.field(
        description=dedent(
            """\
        Model of the modified entity.

        Examples:
        * `"class"`
        * `"employee"`
        * `"org_unit"`
        """
        )
    )

    # UUID of the modified entity
    uuid: UUID = strawberry.field(
        description=dedent(
            """\
        UUID of the modified entity.
        """
        )
    )

    note: str | None = strawberry.field(
        description="Note associated with the registration."
    )

    # The schema never binds to `ModelRegistration` nor any of the concrete
    # implementations of below (i.e. `FacetRegistration`), rather the schema only binds
    # to the interface type (`IRegistration`). To get to the concrete implementations
    # a downcast is performed at run-time using the method below, which is called with
    # the data returned from our `registration_resolver` and which should return the
    # type to downcast to.
    @classmethod
    def resolve_type(
        cls, model: "IRegistration", info: Info, type_def: Any
    ) -> type | str | None:
        # This method can either return the actual types or their stringified names.
        # We have decided to simply return the names to avoid cyclic dependency issues.
        lookup = {
            "address": "AddressRegistration",
            "association": "AssociationRegistration",
            "class": "ClassRegistration",
            "employee": "PersonRegistration",
            "engagement": "EngagementRegistration",
            "facet": "FacetRegistration",
            "itsystem": "ITSystemRegistreration",
            "ituser": "ITUserRegistration",
            "kle": "KLERegistration",
            "leave": "LeaveRegistration",
            "manager": "ManagerRegistration",
            "owner": "OwnerRegistration",
            "org_unit": "OrganisationUnitRegistration",
            "related": "RelatedUnitRegistration",
            "role": "RoleBindingRegistration",
        }
        return lookup.get(model.model)


@strawberry.type
class ModelRegistration(IRegistration, Generic[MOObject]):
    # This object is instantiated when `IRegistration`'s `resolve_type` has resolved
    # to one of its concrete implementations (i.e. `FacetRegistration`), once this
    # happens Strawberry performs a sanity check to ensure that the resolved-type is
    # actually the type that has been constructed by the resolver
    # (i.e. `registration_resolver`).
    #
    # In our case this is not the case, as the `registration_resolver` does not
    # construct our concrete registration types directly (i.e. `FacetRegistration`),
    # but rather construct the generic `Registration` which we then downcast using
    # `resolve_type`, thus the default implementation of the `is_type_of` fails.
    #
    # Instead of trying to reimplement Strawberry's downcasting logic inside of our
    # `registration_resolver`, we will simply override `is_type_of` to disable the
    # sanity-check, in effect saying "trust `resolve_type`".
    @classmethod
    def is_type_of(cls, model: IRegistration, info: Info) -> bool:
        # We trust resolve_type made the right choice
        return True


# These concrete classes must be instantiated explicitly so they can be added to the
# `types` parameter on `CustomSchema` within `schema.py` as strawberry otherwise has no
# way to discover which instantiations of `ModelRegistration` may exist and thus cannot
# construct the schema statically.


@strawberry.type
class AddressRegistration(ModelRegistration[Address]):
    pass


@strawberry.type
class AssociationRegistration(ModelRegistration[Association]):
    pass


@strawberry.type
class ClassRegistration(ModelRegistration[Class]):
    pass


@strawberry.type
class PersonRegistration(ModelRegistration[Employee]):
    pass


@strawberry.type
class EngagementRegistration(ModelRegistration[Engagement]):
    pass


@strawberry.type
class FacetRegistration(ModelRegistration[Facet]):
    pass


@strawberry.type
class ITSystemRegistration(ModelRegistration[ITSystem]):
    pass


@strawberry.type
class ITUserRegistration(ModelRegistration[ITUser]):
    pass


@strawberry.type
class KLERegistration(ModelRegistration[KLE]):
    pass


@strawberry.type
class LeaveRegistration(ModelRegistration[Leave]):
    pass


@strawberry.type
class ManagerRegistration(ModelRegistration[Manager]):
    pass


@strawberry.type
class OwnerRegistration(ModelRegistration[Owner]):
    pass


@strawberry.type
class OrganisationUnitRegistration(ModelRegistration[OrganisationUnit]):
    pass


@strawberry.type
class RelatedUnitRegistration(ModelRegistration[RelatedUnit]):
    pass


@strawberry.type
class RoleBindingRegistration(ModelRegistration[RoleBinding]):
    pass
