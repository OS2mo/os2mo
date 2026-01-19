# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Leave."""

from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo.details import LeaveRead

from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyEngagement
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import engagement_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import to_arbitrary_only
from .utils import to_list
from .utils import to_one


@strawberry.experimental.pydantic.type(
    model=LeaveRead,
    description=dedent(
        """
        A leave of absence for an employee.

        Can be everything from a pregnancy or maternity leave to a furlough or a garden leave.
        The `leave_type` can be used to determine the type of leave in question.
        """
    ),
)
class Leave:
    leave_type_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.leave_type_uuid),
        description=dedent(
            """
            The kind of leave of absence.

            Examples:
            * \"Maternity leave\"  <-- This is the only problematic escape sequence
            * \"Parental leave\"
            * \"Furlough\"
            * \"Garden Leave\"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    leave_type: LazyClass = strawberry.field(
        resolver=to_one(
            seed_resolver(
                class_resolver, {"uuids": lambda root: [root.leave_type_uuid]}
            )
        ),
        description=dedent(
            """
            The kind of leave of absence.

            Examples:
            * \"Maternity leave\" <-- This is the only problematic escape sequence
            * \"Parental leave\"
            * \"Furlough\"
            * \"Garden Leave\"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'leave_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    employee: list[LazyEmployee] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                employee_resolver, {"uuids": lambda root: uuid2list(root.employee_uuid)}
            )
        ),
        description=dedent(
            """
            The absent employee.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo.",
    )

    person_response: Response[LazyEmployee] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="employee", uuid=root.employee_uuid),
        description=dedent(
            """
            The absent person.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    person: list[LazyEmployee] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                employee_resolver, {"uuids": lambda root: uuid2list(root.employee_uuid)}
            )
        ),
        description=dedent(
            """
            The absent person.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    engagement_response: Response[LazyEngagement] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="engagement", uuid=root.engagement_uuid),
        description=dedent(
            """
            The engagement the employee is absent from.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement: LazyEngagement = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                engagement_resolver,
                {"uuids": lambda root: [root.engagement_uuid]},
            )
        ),
        description=dedent(
            """
            The engagement the employee is absent from.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagement_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `leave`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: LeaveRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: LeaveRead) -> UUID:
        return root.uuid

    # TODO: Document this
    user_key: str = strawberry.auto

    @strawberry.field(
        description="UUID of the KLE number.",
        deprecation_reason=gen_uuid_field_deprecation("leave_type"),
    )
    async def leave_type_uuid(self, root: LeaveRead) -> UUID:
        return root.leave_type_uuid

    @strawberry.field(
        description="UUID of the KLE number.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: LeaveRead) -> UUID:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the KLE number.",
        deprecation_reason=gen_uuid_field_deprecation("engagement"),
    )
    async def engagement_uuid(self, root: LeaveRead) -> UUID:
        return root.engagement_uuid

    validity: Validity = strawberry.auto
