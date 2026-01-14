# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - ITSystem and ITUser."""

from functools import partial
from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead

from ..filters import ITSystemFilter
from ..filters import ITUserFilter
from ..lazy import LazyAddress
from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyEngagement
from ..lazy import LazyITSystem
from ..lazy import LazyOrganisationUnit
from ..lazy import LazyRoleBinding
from ..models import AddressRead
from ..models import ClassRead
from ..models import RoleBindingRead
from ..paged import Paged
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import address_resolver
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import engagement_resolver
from ..resolvers import it_system_resolver
from ..resolvers import organisation_unit_resolver
from ..resolvers import rolebinding_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import OpenValidity
from ..validity import Validity
from .utils import force_none_return_wrapper
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import raise_force_none_return_if_uuid_none
from .utils import to_list
from .utils import to_one
from .utils import to_only
from .utils import to_paged_response
from .utils import to_response_list


@strawberry.experimental.pydantic.type(
    model=ITSystemRead,
    description="Systems that IT users are connected to",
)
class ITSystem:
    # TODO: Allow querying all accounts

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `itsystem`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ITSystemRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: ITSystemRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
        Human readable name of the itsystem.

        This is the value that should be shown to users in UIs.

        Examples:
        * "SAP"
        * "Active Directory"
        * "SD UUID"
        """
        )
    )
    async def name(self, root: ITSystemRead) -> str:
        return root.name

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to be set to the key used in external systems.

            Examples:
            * "sap_user_uuid"
            * "ad_guid"
            * "sd_employee_uuid"
            """
        )
    )
    async def user_key(self, root: ITSystemRead) -> str:
        return root.user_key

    roles_response: Paged[Response[LazyClass]] = strawberry.field(
        resolver=to_paged_response(ClassRead)(
            seed_resolver(
                class_resolver,
                {
                    "it_system": lambda root: ITSystemFilter(
                        uuids=uuid2list(root.uuid),
                        # The following two arguments are not strictly necessary because
                        # we are filtering by UUIDs which handles dates differently than
                        # normal filters.
                        # If we were to instead filter by say 'user_keys' the arguments
                        # would be necessary. They are added here anyway to simplify the
                        # migration in the future when our filtering achieve consistent
                        # behavior across all filters.
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description=dedent(
            """
            Rolebinding roles related to the IT-system.

            Examples of user-keys:
            * "AD Read"
            * "AD Write"
            * "SAP Admin"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    roles: list[Response[LazyClass]] = strawberry.field(
        resolver=to_response_list(ClassRead)(  # type: ignore
            seed_resolver(
                class_resolver,
                {
                    "it_system": lambda root: ITSystemFilter(
                        uuids=uuid2list(root.uuid),
                        # The following two arguments are not strictly necessary because
                        # we are filtering by UUIDs which handles dates differently than
                        # normal filters.
                        # If we were to instead filter by say 'user_keys' the arguments
                        # would be necessary. They are added here anyway to simplify the
                        # migration in the future when our filtering achieve consistent
                        # behavior across all filters.
                        from_date=None,
                        to_date=None,
                    )
                },
            )
        ),
        description=dedent(
            """
            Rolebinding roles related to the IT-system.

            Examples of user-keys:
            * "AD Read"
            * "AD Write"
            * "SAP Admin"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'roles_response' instead. Will be removed in a future version of OS2mo.",
    )

    # TODO: Document this
    system_type: str | None = strawberry.auto

    validity: OpenValidity = strawberry.auto


@strawberry.experimental.pydantic.type(
    model=ITUserRead,
    description=dedent(
        """
        User information related to IT systems.

        This is commonly used to map out IT accounts or IT service accounts.
        It is however also used to hold IT system specific identifiers for correlation purposes.
        """
    ),
)
class ITUser:
    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: ITUserRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to the key used in external systems.

            Examples:
            * "KarK"
            * "AnkS"
            * "XSIMP"
            * "04184cb6-a5de-47e6-8a08-03cae9ee4c54"
            """
        )
    )
    async def user_key(self, root: ITUserRead) -> str:
        return root.user_key

    @strawberry.field(description="ID of the user account in the external system.")
    async def external_id(self, root: ITUserRead) -> str | None:
        return root.external_id

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
            Employee using the IT account.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo.",
    )

    person_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=EmployeeRead, uuid=root.employee_uuid)
        if root.employee_uuid
        else None,
        description=dedent(
            """
            Person using the IT account.

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
            Person using the IT account.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(
            model=OrganisationUnitRead, uuid=root.org_unit_uuid
        )
        if root.org_unit_uuid
        else None,
        description=dedent(
            """
            Organisation unit using the IT account.

            This is mostly set for service accounts.

            Note:
            This field is mutually exclusive with the `org_unit` field.
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
            Organisation unit using the IT account.

            This is mostly set for service accounts.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    engagements_responses: Paged[Response[LazyEngagement]] = strawberry.field(
        resolver=to_paged_response(EngagementRead)(
            seed_resolver(
                engagement_resolver,
                {"uuids": lambda root: root.engagement_uuids},
            )
        ),
        description=dedent(
            """
            Engagement scoping of the account.

            A person may have multiple IT accounts with each account being relevant for any number of engagement.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagements: list[Response[LazyEngagement]] = strawberry.field(
        resolver=to_response_list(EngagementRead)(  # type: ignore
            seed_resolver(
                engagement_resolver,
                {"uuids": lambda root: root.engagement_uuids},
            )
        ),
        description=dedent(
            """
            Engagement scoping of the account.

            A person may have multiple IT accounts with each account being relevant for any number of engagement.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagements_response' instead. Will be removed in a future version of OS2mo.",
    )

    engagement_response: Response[LazyEngagement] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=EngagementRead, uuid=root.engagement_uuid)
        if root.engagement_uuid
        else None,
        description=dedent(
            """
            Engagement scoping of the account.

            A person may have multiple IT accounts with each account being relevant for only a single engagement.
            This field allows scoping IT accounts such that it is obvious which engagement has given which it-access.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    engagement_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.engagement_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Engagement scoping of the account.

            A person may have multiple IT accounts with each account being relevant for only a single engagement.
            This field allows scoping IT accounts such that it is obvious which engagement has given which it-access.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagement_response' instead. Will be removed in a future version of OS2mo.",
    )

    addresses_response: Paged[Response[LazyAddress]] = strawberry.field(
        resolver=to_paged_response(AddressRead)(
            seed_resolver(
                address_resolver,
                {"ituser": lambda root: ITUserFilter(uuids=[root.uuid])},
            )
        ),
        description=dedent(
            """
            Addresses connected with the IT-user.

            Commonly contain addresses such as:
            * Email
            * AD GUID
            * FK-org UUID
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
    )

    addresses: list[LazyAddress] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                address_resolver,
                {"ituser": lambda root: ITUserFilter(uuids=[root.uuid])},
            )
        ),
        description=dedent(
            """
            Addresses connected with the IT-user.

            Commonly contain addresses such as:
            * Email
            * AD GUID
            * FK-org UUID
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("address")],
        deprecation_reason="Use 'addresses_response' instead. Will be removed in a future version of OS2mo.",
    )

    itsystem_response: Response[LazyITSystem] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ITSystemRead, uuid=root.itsystem_uuid)
        if root.itsystem_uuid
        else None,
        description=dedent(
            """
            ITSystem this account is for.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
    )

    itsystem: LazyITSystem = strawberry.field(
        resolver=to_one(
            seed_resolver(
                it_system_resolver, {"uuids": lambda root: [root.itsystem_uuid]}
            )
        ),
        description=dedent(
            """
            ITSystem this account is for.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("itsystem")],
        deprecation_reason="Use 'itsystem_response' instead. Will be removed in a future version of OS2mo.",
    )

    rolebindings_response: Paged[Response[LazyRoleBinding]] = strawberry.field(
        resolver=to_paged_response(RoleBindingRead)(
            seed_resolver(
                rolebinding_resolver,
                {"ituser": lambda root: ITUserFilter(uuids=[root.uuid])},
            )
        ),
        description="Rolebindings this IT User has in the connected IT system.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("rolebinding"),
        ],
    )

    rolebindings: list[LazyRoleBinding] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                rolebinding_resolver,
                {"ituser": lambda root: ITUserFilter(uuids=[root.uuid])},
            )
        ),
        description="Rolebindings this IT User has in the connected IT system.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("rolebinding"),
        ],
        deprecation_reason="Use 'rolebindings_response' instead. Will be removed in a future version of OS2mo.",
    )

    primary_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.primary_uuid)
        if root.primary_uuid
        else None,
        description=dedent(
            """
            Marks which IT account is primary.

            When exporting data from OS2mo to external systems, that only support a single IT account, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * "primary"
            * "non-primary"
            * "explicitly-primary"

            It is a convention that at most one IT account for each employee / employee+engagement is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more IT accounts are primary, the entire purpose of the field breaks down.
            In the future this convention may become an invariant.
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
            Marks which IT account is primary.

            When exporting data from OS2mo to external systems, that only support a single IT account, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * "primary"
            * "non-primary"
            * "explicitly-primary"

            It is a convention that at most one IT account for each employee / employee+engagement is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more IT accounts are primary, the entire purpose of the field breaks down.
            In the future this convention may become an invariant.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'primary_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `it`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: ITUserRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(
        description="UUID of the ITSystem related to the user.",
        deprecation_reason=gen_uuid_field_deprecation("itsystem"),
    )
    async def itsystem_uuid(self, root: ITUserRead) -> UUID:
        return root.itsystem_uuid

    @strawberry.field(
        description="UUID of the employee related to the user.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: ITUserRead) -> UUID | None:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the organisation unit related to the user.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: ITUserRead) -> UUID | None:
        return root.org_unit_uuid

    @strawberry.field(
        description="UUID of the engagement related to the user.",
        deprecation_reason="Use `engagement_uuids` instead.",
    )
    async def engagement_uuid(self, root: ITUserRead) -> UUID | None:
        return root.engagement_uuid

    @strawberry.field(
        description="UUIDs of the engagements related to the user.",
        deprecation_reason=gen_uuid_field_deprecation("engagements"),
    )
    async def engagement_uuids(self, root: ITUserRead) -> list[UUID]:
        return root.engagement_uuids

    @strawberry.field(
        description="UUID of the primary klasse of the user.",
        deprecation_reason=gen_uuid_field_deprecation("primary"),
    )
    async def primary_uuid(self, root: ITUserRead) -> UUID | None:
        return root.primary_uuid

    validity: Validity = strawberry.auto
