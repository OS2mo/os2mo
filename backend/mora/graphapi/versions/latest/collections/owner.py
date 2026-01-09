# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Owner."""

from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import OwnerRead

from ..lazy import LazyEmployee
from ..lazy import LazyOrganisationUnit
from ..models import OwnerInferencePriority
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import employee_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..validity import Validity
from .utils import force_none_return_wrapper
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import raise_force_none_return_if_uuid_none
from .utils import to_list


@strawberry.experimental.pydantic.type(
    model=OwnerRead,
    description=dedent(
        """
        Owner of organisation units/employees and their connected identities.
        """
    ),
)
class Owner:
    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `owner`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: OwnerRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: OwnerRead) -> UUID:
        return root.uuid

    # TODO: Document this
    user_key: str = strawberry.auto

    org_unit_response: Response[LazyOrganisationUnit] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(
            model=OrganisationUnitRead, uuid=root.org_unit_uuid
        )
        if root.org_unit_uuid
        else None,
        description=dedent(
            """
            The owned organisation unit.

            Note:
            This field is mutually exclusive with the `employee` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    organisation_unit_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.org_unit_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            The owned organisation unit.

            Note:
            This field is mutually exclusive with the `employee` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description="UUID of the organisation unit related to the owner.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: OwnerRead) -> UUID | None:
        return root.org_unit_uuid

    person_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=EmployeeRead, uuid=root.employee_uuid)
        if root.employee_uuid
        else None,
        description=dedent(
            """
            The owned person.

            Note:
            This field is mutually exclusive with the `org_unit` field.
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
            The owned person.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description="UUID of the employee related to the owner.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: OwnerRead) -> UUID | None:
        return root.employee_uuid

    owner_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=EmployeeRead, uuid=root.owner_uuid)
        if root.owner_uuid
        else None,
        description=dedent(
            """
        Owner of the connected person or organisation unit.
        """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
    )

    owner: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    employee_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.owner_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
        Owner of the connected person or organisation unit.
        """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("owner")],
        deprecation_reason="Use 'owner_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description="UUID of the owner.",
        deprecation_reason=gen_uuid_field_deprecation("owner"),
    )
    async def owner_uuid(self, root: OwnerRead) -> UUID | None:
        return root.owner_uuid

    owner_inference_priority: OwnerInferencePriority | None = strawberry.field(
        description=dedent(
            """
        Inference priority, if set: `engagement_priority` or `association_priority`
        """
        )
    )

    validity: Validity = strawberry.auto
