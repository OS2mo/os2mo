# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Manager."""

from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo.details import ManagerRead

from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyOrganisationUnit
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import force_none_return_wrapper
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import raise_force_none_return_if_uuid_none
from .utils import to_arbitrary_only
from .utils import to_list
from .utils import to_paged_response


@strawberry.experimental.pydantic.type(
    model=ManagerRead,
    description=dedent(
        """
        Managers of organisation units and their connected identities.
        """
    ),
)
class Manager:
    manager_type_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.manager_type_uuid)
        if root.manager_type_uuid
        else None,
        description=dedent(
            """
            Title of the manager.

            Examples:
            * "Director"
            * "Area manager"
            * "Center manager"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    manager_type: LazyClass = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.manager_type_uuid)},
            )
        ),
        description=dedent(
            """
            Title of the manager.

            Examples:
            * "Director"
            * "Area manager"
            * "Center manager"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'manager_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    manager_level_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.manager_level_uuid)
        if root.manager_level_uuid
        else None,
        # TODO: Check production system values
        description=dedent(
            """
            Hierarchical level of the manager.

            Examples:
            * "Level 1"
            * "Level 2"
            * "Level 3"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    manager_level: LazyClass = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.manager_level_uuid)},
            )
        ),
        # TODO: Check production system values
        description=dedent(
            """
            Hierarchical level of the manager.

            Examples:
            * "Level 1"
            * "Level 2"
            * "Level 3"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'manager_level_response' instead. Will be removed in a future version of OS2mo.",
    )

    responsibilities_response: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response("class")(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: root.responsibility_uuids or []},
            )
        ),
        description=dedent(
            """
            Responsibilities that the manager takes care of.

            Examples:
            * `["Responsible for buildings and areas"]`
            * `["Responsible for buildings and areas", "Staff: Sick leave"]`
            * `[]`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    responsibilities: list[LazyClass] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: root.responsibility_uuids or []},
            )
        ),
        description=dedent(
            """
            Responsibilities that the manager takes care of.

            Examples:
            * `["Responsible for buildings and areas"]`
            * `["Responsible for buildings and areas", "Staff: Sick leave"]
            * `[]`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'responsibilities_response' instead. Will be removed in a future version of OS2mo.",
    )

    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    employee_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.employee_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Employee fulfilling the managerial position.

            May be empty in which case the managerial position is unfilfilled (vacant).
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo.",
    )

    person_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="employee", uuid=root.employee_uuid)
        if root.employee_uuid
        else None,
        description=dedent(
            """
            Person fulfilling the managerial position.

            May be empty in which case the managerial position is unfilfilled (vacant).
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    person: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    employee_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.employee_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Person fulfilling the managerial position.

            May be empty in which case the managerial position is unfilfilled (vacant).
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(
            model="org_unit", uuid=root.org_unit_uuid
        ),
        description=dedent(
            """
            Organisation unit being managed.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                organisation_unit_resolver,
                {"uuids": lambda root: [root.org_unit_uuid]},
            )
        ),
        description=dedent(
            """
            Organisation unit being managed.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `manager`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ManagerRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: ManagerRead) -> UUID:
        return root.uuid

    # TODO: Document this
    user_key: str = strawberry.auto

    @strawberry.field(
        description="UUID of the organisation unit related to the manager.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: ManagerRead) -> UUID:
        return root.org_unit_uuid

    @strawberry.field(
        description="UUID of the employee related to the manager.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: ManagerRead) -> UUID | None:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the manager type.",
        deprecation_reason=gen_uuid_field_deprecation("manager_type"),
    )
    async def manager_type_uuid(self, root: ManagerRead) -> UUID | None:
        return root.manager_type_uuid

    @strawberry.field(
        description="UUID of the manager level.",
        deprecation_reason=gen_uuid_field_deprecation("manager_level"),
    )
    async def manager_level_uuid(self, root: ManagerRead) -> UUID | None:
        return root.manager_level_uuid

    @strawberry.field(
        description="List of UUID's of the responsibilities.",
        deprecation_reason=gen_uuid_field_deprecation("responsibilities"),
    )
    async def responsibility_uuids(self, root: ManagerRead) -> list[UUID] | None:
        return root.responsibility_uuids

    validity: Validity = strawberry.auto
