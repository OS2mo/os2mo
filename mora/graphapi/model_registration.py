# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime
from inspect import signature
from textwrap import dedent
from typing import Concatenate
from typing import Generic
from typing import ParamSpec
from typing import TypeVar

import strawberry

from .collections import KLE
from .collections import Address
from .collections import Association
from .collections import Class
from .collections import Employee
from .collections import Engagement
from .collections import Facet
from .collections import ITSystem
from .collections import ITUser
from .collections import Leave
from .collections import Manager
from .collections import OrganisationUnit
from .collections import Owner
from .collections import RelatedUnit
from .collections import RoleBinding
from .moobject import MOObject
from .registrationbase import RegistrationBase
from .response import HasUUIDModel
from .response import current_resolver
from .response import validity_resolver

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class HasStart(HasUUIDModel):
    start: datetime | None


def registration_time_decorator(
    resolver_func: Callable[Concatenate[HasUUIDModel, P], Awaitable[R]],
) -> Callable[Concatenate[HasStart, P], Awaitable[R]]:
    async def inner(root: HasStart, *args: P.args, **kwargs: P.kwargs) -> R:
        return await resolver_func(
            root,
            *args,
            registration_time=root.start,  # type: ignore[arg-type]
            **kwargs,
        )

    # Remove the configured parameters from our signature ensuring they cannot be set by
    # the GraphQL caller and thus always get called with their default values.
    sig = signature(resolver_func)
    parameters = sig.parameters.copy()
    parameters.pop("registration_time")
    new_sig = sig.replace(parameters=list(parameters.values()))
    # Update our signature and return the stripped resolver function
    inner.__signature__ = new_sig  # type: ignore[attr-defined]
    return inner


@strawberry.interface(
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
class IRegistration(RegistrationBase):
    pass


@strawberry.type
class ModelRegistration(IRegistration, Generic[MOObject]):
    # NOTE: The `current` and `validities` field also occur on `Response`.
    current: MOObject | None = strawberry.field(
        description=dedent(
            """\
            Actual / current state entrypoint.

            Returns the state of the object at current validity and current assertion time.

            A single object is returned as only one validity can be active at a given assertion time.

            Note:
            This the entrypoint is appropriate to use for actual-state integrations and UIs.
            """
        ),
        resolver=registration_time_decorator(current_resolver),
    )

    validities: list[MOObject] = strawberry.field(
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
        resolver=registration_time_decorator(validity_resolver),
    )


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
