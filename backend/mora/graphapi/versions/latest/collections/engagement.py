# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Engagement."""

from collections.abc import Callable
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID

import strawberry
from strawberry.types import Info

from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.service.facet import is_class_uuid_primary

from ..filters import EmployeeFilter
from ..filters import EngagementFilter
from ..filters import ManagerFilter
from ..filters import OrganisationUnitFilter
from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyITUser
from ..lazy import LazyLeave
from ..lazy import LazyManager
from ..lazy import LazyOrganisationUnit
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import it_user_resolver
from ..resolvers import leave_resolver
from ..resolvers import manager_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import get_bound_filter
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import to_arbitrary_only
from .utils import to_list
from .utils import to_only
from .utils import to_paged_response
from .utils import to_response_list


@strawberry.experimental.pydantic.type(
    model=EngagementRead,
    description="Employee engagement in an organisation unit",
)
class Engagement:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: EngagementRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to the `id` used in external systems.

            Examples:
            * `"11009"`
            * `"02782"`
            """
        )
    )
    async def user_key(self, root: EngagementRead) -> str:
        return root.user_key

    engagement_type_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.engagement_type_uuid),
        description=dedent(
            """
            Describes the employee's affiliation to an organisation unit

            Examples:
            * `"Employed"`
            * `"Social worker"`
            * `"Employee (hourly wage)"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    engagement_type: LazyClass = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: [root.engagement_type_uuid]},
            )
        ),
        description=dedent(
            """
            Describes the employee's affiliation to an organisation unit

            Examples:
            * `"Employed"`
            * `"Social worker"`
            * `"Employee (hourly wage)"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'engagement_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    job_function_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.job_function_uuid),
        description=dedent(
            """
            Describes the position of the employee in the organisation unit

            Examples:
            * `"Payroll consultant"`
            * `"Office student"`
            * `"Jurist"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    job_function: LazyClass = strawberry.field(
        resolver=to_arbitrary_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: [root.job_function_uuid]},
            )
        ),
        description=dedent(
            """
            Describes the position of the employee in the organisation unit

            Examples:
            * `"Payroll consultant"`
            * `"Office student"`
            * `"Jurist"`
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'job_function_response' instead. Will be removed in a future version of OS2mo.",
    )

    primary_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.primary_uuid)
        if root.primary_uuid
        else None,
        description=dedent(
            """
            Marks which engagement is primary.

            When exporting data from OS2mo to external systems, that only support a single engagement or associations, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * `"primary"`
            * `"non-primary"`
            * `"explicitly-primary"`

            It is a convention that at most one engagement for each employee is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more engagements are primary, the entire purpose of the field breaks down.
            In the future this convention may become an invariant.

            Note:
            The calculate-primary integration can be used to automatically calculate and update primarity fields.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    primary: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver, {"uuids": lambda root: uuid2list(root.primary_uuid)}
            )
        ),
        description=dedent(
            """
            Marks which engagement is primary.

            When exporting data from OS2mo to external systems, that only support a single engagement or associations, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * `"primary"`
            * `"non-primary"`
            * `"explicitly-primary"`

            It is a convention that at most one engagement for each employee is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more engagements are primary, the entire purpose of the field breaks down.
            In the future this convention may become an invariant.

            Note:
            The calculate-primary integration can be used to automatically calculate and update primarity fields.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'primary_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
        Whether this engagement is the primary engagement.

        Checks if the `primary` field contains either a class with user-key: `"primary"` or `"explicitly-primary"`.
        """
        )
    )
    async def is_primary(self, root: EngagementRead, info: Info) -> bool:
        if not root.primary_uuid:
            return False
        # TODO: Eliminate is_class_uuid_primary lookup by using the above resolver
        #       Then utilize is_class_primary as result_translation
        return await is_class_uuid_primary(str(root.primary_uuid))

    leave_response: Response[LazyLeave] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="leave", uuid=root.leave_uuid)
        if root.leave_uuid
        else None,
        description="Related leave",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
    )

    leave: LazyLeave | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                leave_resolver, {"uuids": lambda root: uuid2list(root.leave_uuid)}
            )
        ),
        description="Related leave",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("leave")],
        deprecation_reason="Use 'leave_response' instead. Will be removed in a future version of OS2mo.",
    )

    employee: list[LazyEmployee] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                employee_resolver, {"uuids": lambda root: uuid2list(root.employee_uuid)}
            )
        ),
        description=dedent(
            """
            The employee fulfilling the engagement.
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
            The person fulfilling the engagement.
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
            The person fulfilling the engagement.
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
            The organisation unit where the engagement is being fulfilled.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_unit: list[LazyOrganisationUnit] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                organisation_unit_resolver,
                {"uuids": lambda root: uuid2list(root.org_unit_uuid)},
            )
        ),
        description=dedent(
            """
            The organisation unit where the engagement is being fulfilled.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    itusers_response: Paged[Response[LazyITUser]] = strawberry.field(
        resolver=to_paged_response("ituser")(
            seed_resolver(
                it_user_resolver,
                {
                    "engagement": lambda root: EngagementFilter(
                        uuids=[root.uuid],
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description="Connected IT-user.\n",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    itusers: list[Response[LazyITUser]] = strawberry.field(
        resolver=to_response_list(ITUserRead)(  # type: ignore
            seed_resolver(
                it_user_resolver,
                {
                    "engagement": lambda root: EngagementFilter(
                        uuids=[root.uuid],
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description="Connected IT-user.\n",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'itusers_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `engagement`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: EngagementRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(
        description="UUID of the engagement type class.",
        deprecation_reason=gen_uuid_field_deprecation("engagement_type"),
    )
    async def engagement_type_uuid(self, root: EngagementRead) -> UUID:
        return root.engagement_type_uuid

    @strawberry.field(
        description="UUID of the employee related to the engagement.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: EngagementRead) -> UUID:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the organisation unit related to the engagement.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: EngagementRead) -> UUID:
        return root.org_unit_uuid

    @strawberry.field(
        description="UUID of the job function class.",
        deprecation_reason=gen_uuid_field_deprecation("job_function"),
    )
    async def job_function_uuid(self, root: EngagementRead) -> UUID:
        return root.job_function_uuid

    @strawberry.field(
        description="UUID of the leave related to the engagement.",
        deprecation_reason=gen_uuid_field_deprecation("leave"),
    )
    async def leave_uuid(self, root: EngagementRead) -> UUID | None:
        return root.leave_uuid

    @strawberry.field(
        description="UUID of the primary klasse of the engagement.",
        deprecation_reason=gen_uuid_field_deprecation("primary"),
    )
    async def primary_uuid(self, root: EngagementRead) -> UUID | None:
        return root.primary_uuid

    # TODO: Add Paged[Response[LazyClass]] managers_response
    @strawberry.field(
        description=dedent(
            """
            Managerial roles for the engagement's organisation unit.

            May be empty in which case managers are usually inherited from parents.
            See the `inherit`-flag for details.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("manager")],
    )
    async def managers(
        self,
        info: Info,
        root: EngagementRead,
        # NOTE: Using get_bound_filter to ensure the filter type is the same as for org_unit.managers
        filter: get_bound_filter(ManagerFilter, frozenset({"org_units"})) | None = None,  # type: ignore
        # NOTE: Description copied from manager_resolver
        inherit: Annotated[
            bool,
            strawberry.argument(
                description=dedent(
                    """
                    Whether to inherit managerial roles or not.

                    If managerial roles exist directly on this organisation unit, the flag does nothing and these managerial roles are returned.
                    However if no managerial roles exist directly, and this flag is:
                    * False: An empty list is returned.
                    * True: The result from calling `managers` with `inherit=True` on the parent of this organistion unit is returned.

                    Calling with `inherit=True` can help ensure that a manager is always found.
                    """
                )
            ),
        ] = False,
        exclude_self: Annotated[
            bool,
            strawberry.argument(
                description=dedent(
                    """
                    Whether to exclude the employee self when inheriting managerial roles.

                    If set to `true` the employee self will never be returned in the managers list.

                    If both this and `inherit` is set to `true` the organization tree will be traversed, to find the first manager that is not the employee self.
                    """
                )
            ),
        ] = False,
    ) -> list[LazyManager]:
        # Recurse up the tree using the parent org-unit
        filter = filter or ManagerFilter()
        seeds: dict[str, Callable[[EngagementRead], Any]] = {
            "org_units": lambda root: None,
            "org_unit": lambda root: OrganisationUnitFilter(
                uuids=uuid2list(root.org_unit_uuid)
            ),
        }
        if exclude_self:
            if filter.exclude:  # pragma: no cover
                raise ValueError("Cannot provide both filter.exclude and exclude_self")
            seeds["exclude"] = lambda root: EmployeeFilter(
                uuids=uuid2list(root.employee_uuid)
            )

        resolver = to_list(seed_resolver(manager_resolver, seeds))
        return await resolver(root=root, info=info, filter=filter, inherit=inherit)

    # TODO: Document this
    fraction: int | None = strawberry.auto

    # TODO: Make structured model for these?
    extension_1: str | None = strawberry.auto
    extension_2: str | None = strawberry.auto
    extension_3: str | None = strawberry.auto
    extension_4: str | None = strawberry.auto
    extension_5: str | None = strawberry.auto
    extension_6: str | None = strawberry.auto
    extension_7: str | None = strawberry.auto
    extension_8: str | None = strawberry.auto
    extension_9: str | None = strawberry.auto
    extension_10: str | None = strawberry.auto

    validity: Validity = strawberry.auto
