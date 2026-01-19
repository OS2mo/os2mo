# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Role Binding."""

from textwrap import dedent
from uuid import UUID

import strawberry

from ..lazy import LazyClass
from ..lazy import LazyITUser
from ..lazy import LazyOrganisationUnit
from ..models import RoleBindingRead
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import it_user_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import list_to_optional_field_warning
from .utils import to_list


@strawberry.experimental.pydantic.type(
    model=RoleBindingRead,
    description="The role a person has within an organisation unit",
)
class RoleBinding:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: RoleBindingRead) -> UUID:
        return root.uuid

    # TODO: Document this
    user_key: str = strawberry.auto

    role_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.role),
        description=dedent(
            """
            The role that is being fulfilled.

            Examples of user-keys:
            * \"AD Read\"
            * \"AD Write\"
            * \"SAP Admin\"
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    role: list[LazyClass] = strawberry.field(
        resolver=to_list(
            seed_resolver(class_resolver, {"uuids": lambda root: [root.role]})
        ),
        description=dedent(
            """
            The role that is being fulfilled.

            Examples of user-keys:
            * \"AD Read\"
            * \"AD Write\"
            * \"SAP Admin\"
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'role_response' instead. Will be removed in a future version of OS2mo.",
    )

    ituser_response: Response[LazyITUser] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="ituser", uuid=root.it_user_uuid),
        description="The IT-user that should be granted this role\n"
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    ituser: list[LazyITUser] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                it_user_resolver, {"uuids": lambda root: uuid2list(root.it_user_uuid)}
            )
        ),
        description="The IT-user that should be granted this role\n"
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'ituser_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="org_unit", uuid=root.org_unit_uuid)
        if root.org_unit_uuid
        else None,
        description=dedent(
            """
            The organisational unit in which the role is being fulfilled.
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
            The organisational unit in which the role is being fulfilled.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    validity: Validity = strawberry.auto
