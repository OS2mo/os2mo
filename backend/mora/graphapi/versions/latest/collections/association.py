# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Association."""

from textwrap import dedent
from uuid import UUID

import strawberry

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.handler.reading import get_handler_for_type

from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyITUser
from ..lazy import LazyOrganisationUnit
from ..models import ClassRead
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import it_user_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import to_list
from .utils import to_only
from .utils import validity_sub_query_hack


@strawberry.experimental.pydantic.type(
    model=AssociationRead,
    description="Connects organisation units and employees",
)
class Association:
    association_type_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.association_type_uuid)
        if root.association_type_uuid
        else None,
        description=dedent(
            """
            The type of connection that the employee has to the organisation unit.

            Examples:
            * "Chairman"
            * "Leader"
            * "Employee"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    association_type: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.association_type_uuid)},
            )
        ),
        description=dedent(
            """
            The type of connection that the employee has to the organisation unit.

            Examples:
            * "Chairman"
            * "Leader"
            * "Employee"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'association_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    dynamic_class_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.dynamic_class_uuid)
        if root.dynamic_class_uuid
        else None,
        # TODO: Document this
        # https://git.magenta.dk/rammearkitektur/os2mo/-/merge_requests/1694#note_216859
        description=dedent(
            """
            List of arbitrary classes.

            The purpose of this field is ill-defined.
            It is currently mainly used for (trade) union specification.
            """
        ),
        deprecation_reason=dedent(
            """
            Will be removed in a future version of GraphQL.
            Currently no replacement is in place, but specialized fields will probably arive in the future.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    dynamic_class: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.dynamic_class_uuid)},
            )
        ),
        # TODO: Document this
        # https://git.magenta.dk/rammearkitektur/os2mo/-/merge_requests/1694#note_216859
        description=dedent(
            """
            List of arbitrary classes.

            The purpose of this field is ill-defined.
            It is currently mainly used for (trade) union specification.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'dynamic_class_response' instead. Will be removed in a future version of OS2mo.",
    )

    trade_union_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.dynamic_class_uuid)
        if root.dynamic_class_uuid
        else None,
        description=dedent(
            """
            Marks associations with a trade union
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    trade_union: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.dynamic_class_uuid)},
            )
        ),
        description=dedent(
            """
            Marks associations with a trade union
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'trade_union_response' instead. Will be removed in a future version of OS2mo.",
    )

    primary_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.primary_uuid)
        if root.primary_uuid
        else None,
        description=dedent(
            """
            Marks which association is primary.

            When exporting data from OS2mo to external systems, that only support a single engagement or associations, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * "primary"
            * "non-primary"
            * "explicitly-primary"

            It is a convention that at most one association for each employee is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more associations are primary, the entire purpose of the field breaks down.
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
            Marks which association is primary.

            When exporting data from OS2mo to external systems, that only support a single engagement or associations, this field can be used to export the primary one.
            What primarity means is vaguely defined, but usually derived from workload or time-allocation.

            Examples  of user-keys:
            * "primary"
            * "non-primary"
            * "explicitly-primary"

            It is a convention that at most one association for each employee is set as either `primary` or `explicitly-primary`.
            This convention is in place as if more associations are primary, the entire purpose of the field breaks down.
            In the future this convention may become an invariant.

            Note:
            The calculate-primary integration can be used to automatically calculate and update primarity fields.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'primary_response' instead. Will be removed in a future version of OS2mo.",
    )

    employee: list[LazyEmployee] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                employee_resolver, {"uuids": lambda root: uuid2list(root.employee_uuid)}
            )
        ),
        description=dedent(
            """
            Associated employee.
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
            Associated person.
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
            Associated person.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(
            model=OrganisationUnitRead, uuid=root.org_unit_uuid
        ),
        description=dedent(
            """
            Associated organisation unit.
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
            Associated organisation unit.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    substitute_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=EmployeeRead, uuid=root.substitute_uuid)
        if root.substitute_uuid
        else None,
        description=dedent(
            """
            Optional substitute if `employee` is unavailable.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    substitute: list[LazyEmployee] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                employee_resolver,
                {"uuids": lambda root: uuid2list(root.substitute_uuid)},
            )
        ),
        description=dedent(
            """
            Optional subsitute if `employee` is unavailable.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'subsitute_response' instead. Will be removed in a future version of OS2mo.",
    )

    job_function_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ClassRead, uuid=root.job_function_uuid)
        if root.job_function_uuid
        else None,
        description=dedent(
            """
            The position held by the employee in the organisation unit.

            Examples of user-keys:
            * "Payroll consultant"
            * "Office student"
            * "Jurist"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    job_function: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver,
                {"uuids": lambda root: uuid2list(root.job_function_uuid)},
            )
        ),
        description=dedent(
            """
            The position held by the employee in the organisation unit.

            Examples of user-keys:
            * "Payroll consultant"
            * "Office student"
            * "Jurist"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'job_function_response' instead. Will be removed in a future version of OS2mo.",
    )

    it_user_response: Response[LazyITUser] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model=ITUserRead, uuid=root.it_user_uuid)
        if root.it_user_uuid
        else None,
        description=dedent(
            """
            The IT-user utilized by the employee when fulfilling the association responsibilities.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    it_user: list[LazyITUser] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                it_user_resolver, {"uuids": lambda root: uuid2list(root.it_user_uuid)}
            )
        ),
        description=dedent(
            """
            The IT-user utilized by the employee when fulfilling the association responsibilities.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'it_user_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `association`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: AssociationRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: AssociationRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to be set to the key used in external systems.

            Examples:
            * "1462"
            * "XSIMP"
            """
        )
    )
    async def user_key(self, root: AssociationRead) -> str:
        return root.user_key

    @strawberry.field(
        description="UUID of the dynamically attached class.",
        deprecation_reason=gen_uuid_field_deprecation("dynamic_class"),
    )
    async def dynamic_class_uuid(
        self, root: AssociationRead
    ) -> UUID | None:  # pragma: no cover
        return root.dynamic_class_uuid

    @strawberry.field(
        description="UUID of the attached trade union.",
        deprecation_reason=gen_uuid_field_deprecation("trade_union"),
    )
    async def trade_union_uuid(self, root: AssociationRead) -> UUID | None:
        return root.dynamic_class_uuid

    @strawberry.field(
        description="UUID of the organisation unit related to the association.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: AssociationRead) -> UUID:
        return root.org_unit_uuid

    @strawberry.field(
        description="UUID of the employee related to the association.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: AssociationRead) -> UUID | None:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the association type.",
        deprecation_reason=gen_uuid_field_deprecation("association_type"),
    )
    async def association_type_uuid(self, root: AssociationRead) -> UUID | None:
        return root.association_type_uuid

    @strawberry.field(
        description="UUID of the primary type of the association.",
        deprecation_reason=gen_uuid_field_deprecation("primary"),
    )
    async def primary_uuid(self, root: AssociationRead) -> UUID | None:
        return root.primary_uuid

    @strawberry.field(
        description="UUID of the substitute for the employee in the association.",
        deprecation_reason=gen_uuid_field_deprecation("subsitute"),
    )
    async def substitute_uuid(self, root: AssociationRead) -> UUID | None:
        return root.substitute_uuid

    @strawberry.field(
        description="UUID of a job function class, only defined for 'IT associations.",
        deprecation_reason=gen_uuid_field_deprecation("job_function"),
    )
    async def job_function_uuid(self, root: AssociationRead) -> UUID | None:
        return root.job_function_uuid

    @strawberry.field(
        description="UUID of an 'ITUser' model, only defined for 'IT associations.",
        deprecation_reason=gen_uuid_field_deprecation("it_user"),
    )
    async def it_user_uuid(self, root: AssociationRead) -> UUID | None:
        return root.it_user_uuid

    validity: Validity = strawberry.auto

    # VALIDITY HACKS

    @strawberry.field(
        description=dedent(
            """
            Same as association_type, but with HACKs to enable validities.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("class"),
        ],
        deprecation_reason=dedent(
            """
            Should only be used to query association_types when validity dates have been specified, "
            "ex from_date & to_date."
            "Will be removed when sub-query date handling is implemented.
            """
        ),
    )
    async def association_type_validity(
        self, root: AssociationRead
    ) -> LazyClass | None:  # pragma: no cover
        association_types = await validity_sub_query_hack(
            root.validity,
            ClassRead,
            get_handler_for_type("class"),
            {"uuid": uuid2list(root.association_type_uuid)},
        )

        return association_types[0] if association_types else None
