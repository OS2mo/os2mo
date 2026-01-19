# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Employee."""

from datetime import date
from textwrap import dedent
from typing import cast
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo import EmployeeRead

from ..lazy import LazyAddress
from ..lazy import LazyAssociation
from ..lazy import LazyEngagement
from ..lazy import LazyITUser
from ..lazy import LazyLeave
from ..lazy import LazyManager
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import address_resolver
from ..resolvers import association_resolver
from ..resolvers import engagement_resolver
from ..resolvers import it_user_resolver
from ..resolvers import leave_resolver
from ..resolvers import manager_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..types import CPRType
from ..validity import OpenValidity
from .utils import to_list
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=EmployeeRead,
    description="Employee/identity specific information",
)
class Employee:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: EmployeeRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to be set to the key used in external systems.

            Defaults to the `uuid` generated on object creation.

            Examples:
            * \"1462\"
            * \"XSIMP\"
            """
        )
    )
    async def user_key(self, root: EmployeeRead) -> str:
        return root.user_key

    engagements_response: Paged[Response[LazyEngagement]] = strawberry.field(
        resolver=to_paged_response("engagement")(
            seed_resolver(
                engagement_resolver,
                {"employees": lambda root: [root.uuid]},
            ),
        ),
        description=dedent(
            """
            Engagements for the employee.

            May be an empty list if the employee is not employeed.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagements: list[LazyEngagement] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                engagement_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Engagements for the employee.

            May be an empty list if the employee is not employeed.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagements_response' instead. Will be removed in a future version of OS2mo.",
    )

    manager_roles_response: Paged[Response[LazyManager]] = strawberry.field(
        resolver=to_paged_response("manager")(
            seed_resolver(
                manager_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Managerial roles for the employee.

            Usually an empty list as most employees are not managers.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )

    manager_roles: list[LazyManager] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                manager_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Managerial roles for the employee.

            Usually an empty list as most employees are not managers.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
        deprecation_reason="Use 'manager_roles_response' instead. Will be removed in a future version of OS2mo.",
    )

    addresses_response: Paged[Response[LazyAddress]] = strawberry.field(
        resolver=to_paged_response("address")(
            seed_resolver(
                address_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Addresses for the employee.

            Commonly contain addresses such as, their:
            * Work location
            * Office number
            * Work phone number
            * Work email
            * Personal phone number
            * Personal email
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                address_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Addresses for the employee.

            Commonly contain addresses such as, their:
            * Work location
            * Office number
            * Work phone number
            * Work email
            * Personal phone number
            * Personal email
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
        deprecation_reason="Use 'addresses_response' instead. Will be removed in a future version of OS2mo.",
    )

    leaves_response: Paged[Response[LazyLeave]] = strawberry.field(
        resolver=to_paged_response("leave")(
            seed_resolver(
                leave_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Leaves of absence for the employee.

            Usually empty as most employees are not on leaves of absence.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    leaves: list[LazyLeave] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                leave_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Leaves of absence for the employee.

            Usually empty as most employees are not on leaves of absence.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
        deprecation_reason="Use 'leaves_response' instead. Will be removed in a future version of OS2mo.",
    )

    associations_response: Paged[Response[LazyAssociation]] = strawberry.field(
        resolver=to_paged_response("association")(
            seed_resolver(
                association_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Associations for the employee.

            May be an empty list if the employee is not associated with projects, etc.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
    )

    associations: list[LazyAssociation] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                association_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            Associations for the employee.

            May be an empty list if the employee is not associated with projects, etc.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("association"),
        ],
        deprecation_reason="Use 'associations_response' instead. Will be removed in a future version of OS2mo.",
    )

    itusers_response: Paged[Response[LazyITUser]] = strawberry.field(
        resolver=to_paged_response("ituser")(
            seed_resolver(
                it_user_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            IT accounts for the employee.

            May be an empty list if the employee does not have any IT-access whatsoever.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    itusers: list[LazyITUser] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                it_user_resolver,
                {"employees": lambda root: [root.uuid]},
            )
        ),
        description=dedent(
            """
            IT accounts for the employee.

            May be an empty list if the employee does not have any IT-access whatsoever.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'itusers_response' instead. Will be removed in a future version of OS2mo.",
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

    # TODO: Document this
    cpr_no: CPRType | None = strawberry.field(
        deprecation_reason="Use 'cpr_number' instead. Will be removed in a future version of OS2mo."
    )

    @strawberry.field(description="CPR number of the employee.")
    async def cpr_number(self, root: EmployeeRead) -> CPRType | None:
        return cast(CPRType | None, root.cpr_no)

    # TODO: Document this
    seniority: date | None = strawberry.auto

    # TODO: Deprecate this?
    @strawberry.field(description="Full name of the employee")
    async def name(self, root: EmployeeRead) -> str:
        return f"{root.givenname} {root.surname}".strip()

    givenname: str = strawberry.field(
        deprecation_reason="Use 'given_name' instead. Will be removed in a future version of OS2mo."
    )

    @strawberry.field(description="Given name of the employee.")
    async def given_name(self, root: EmployeeRead) -> str:
        return root.givenname

    surname: str = strawberry.auto

    # TODO: Deprecate this?
    @strawberry.field(description="Full nickname of the employee")
    async def nickname(self, root: EmployeeRead) -> str:
        return f"{root.nickname_givenname} {root.nickname_surname}".strip()

    nickname_givenname: str | None = strawberry.field(
        deprecation_reason="Use 'nickname_given_name' instead. Will be removed in a future version of OS2mo."
    )

    @strawberry.field(description="Given name part of nickname of the employee.")
    async def nickname_given_name(self, root: EmployeeRead) -> str | None:
        return root.nickname_givenname

    nickname_surname: str | None = strawberry.auto

    validity: OpenValidity = strawberry.auto
