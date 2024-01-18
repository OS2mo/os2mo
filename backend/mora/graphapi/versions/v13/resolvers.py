# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Resolver shims, converting from function arguments to a filter object."""
from collections.abc import Callable
from datetime import datetime
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID

import strawberry
from strawberry import UNSET
from strawberry.types import Info

from ..latest.filters import AddressFilter
from ..latest.filters import AssociationFilter
from ..latest.filters import BaseFilter
from ..latest.filters import ClassFilter
from ..latest.filters import ConfigurationFilter
from ..latest.filters import EmployeeFilter
from ..latest.filters import EngagementFilter
from ..latest.filters import FacetFilter
from ..latest.filters import FileFilter
from ..latest.filters import gen_filter_string
from ..latest.filters import gen_filter_table
from ..latest.filters import HealthFilter
from ..latest.filters import ITSystemFilter
from ..latest.filters import ITUserFilter
from ..latest.filters import KLEFilter
from ..latest.filters import LeaveFilter
from ..latest.filters import ManagerFilter
from ..latest.filters import OrganisationUnitFilter
from ..latest.filters import OwnerFilter
from ..latest.filters import RelatedUnitFilter
from ..latest.filters import RoleFilter
from ..latest.models import FileStore
from ..latest.paged import CursorType
from ..latest.paged import LimitType
from ..latest.query import configuration_resolver
from ..latest.query import file_resolver
from ..latest.query import health_resolver
from ..latest.resolvers import address_resolver
from ..latest.resolvers import association_resolver
from ..latest.resolvers import class_resolver
from ..latest.resolvers import employee_resolver
from ..latest.resolvers import engagement_resolver
from ..latest.resolvers import facet_resolver
from ..latest.resolvers import generic_resolver
from ..latest.resolvers import it_system_resolver
from ..latest.resolvers import it_user_resolver
from ..latest.resolvers import kle_resolver
from ..latest.resolvers import leave_resolver
from ..latest.resolvers import manager_resolver
from ..latest.resolvers import organisation_unit_resolver
from ..latest.resolvers import owner_resolver
from ..latest.resolvers import related_unit_resolver
from ..latest.resolvers import role_resolver
from ..v17.version import PagedResolver
from mora.util import CPR
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITSystemRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import OwnerRead
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import RoleRead

UUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("UUID", "uuids")),
]
UserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(description=gen_filter_string("User-key", "user_keys")),
]

FromDateFilterType = Annotated[
    datetime | None,
    strawberry.argument(
        description=dedent(
            """\
    Limit the elements returned by their starting validity.
    """
        )
    ),
]
ToDateFilterType = Annotated[
    datetime | None,
    strawberry.argument(
        description=dedent(
            """\
    Limit the elements returned by their ending validity.
    """
        )
    ),
]

FacetUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Facet UUID", "facets")),
]
FacetUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Facet user-key", "facet_user_keys")
    ),
]

ParentUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Parent UUID", "parents")),
]
ParentUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Parent user-key", "parent_user_keys")
    ),
]

AddressTypeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Address type UUID", "address_types")
    ),
]
AddressTypeUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Address type user-key", "address_type_user_keys")
    ),
]
EmployeeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Employee UUID", "employees")),
]
EngagementUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Engagement UUID", "engagements")
    ),
]
OrgUnitUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Organisational Unit UUID", "org_units")
    ),
]

AssociationTypeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Association type UUID", "association_types")
    ),
]
AssociationTypeUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string(
            "Association type user-key", "association_type_user_keys"
        )
    ),
]

ITAssociation = Annotated[
    bool | None,
    strawberry.argument(
        description=dedent(
            """\
    Query for either IT-Associations or "normal" Associations. `None` returns all.

    This field is needed to replicate the functionality in the service API:
    `?it=1`
    """
        )
    ),
]

CPRNumberFilterType = Annotated[
    list[CPR] | None,
    strawberry.argument(description=gen_filter_string("CPR number", "cpr_numbers")),
]

HierarchiesUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=dedent(
            """\
        Filter organisation units by their organisational hierarchy labels.

        Can be used to extract a subset of the organisational structure.

        Examples of user-keys:
        * `"Line-management"`
        * `"Self-owned institution"`
        * `"Outside organisation"`
        * `"Hidden"`

        Note:
        The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
        """
        )
        + gen_filter_table("hierarchies")
    ),
]


class Resolver(PagedResolver):
    neutral_element_constructor: Callable[[], Any] = dict

    def __init__(self, model: type) -> None:
        """Create a field resolver by specifying a model.

        Args:
            model: The MOModel.
        """
        self.model: type = model

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: BaseFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve a query using the specified arguments.

        Args:
            uuids: Only retrieve these UUIDs. Defaults to None.
            user_keys: Only retrieve these user_keys. Defaults to None.
            limit: The maximum number of elements to return. Fewer elements may be
                returned if the query itself yields fewer elements.
            from_date: Lower bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case from_date is today.
            to_date: Upper bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case to_date is from_date + 1 ms.

        Note:
            While OFFSET and LIMITing is done in LoRa/SQL, further filtering is
            sometimes applied in MO. Confusingly, this means that receiving a list
            shorter than the requested limit does not imply that we are at the end.

        Returns:
            List of response objects based on getters/loaders.

        Note:
            The default behaviour of from_date and to_date, i.e. both being
            UNSET, is equivalent to validity=present in the service API.
        """
        return await self._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )

    async def _resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: BaseFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        **kwargs: Any,
    ):
        """The internal resolve interface, allowing for kwargs."""
        _resolver_tuples = [
            (FacetRead, "facet_getter", "facet_loader"),
            (ClassRead, "class_getter", "class_loader"),
            (AddressRead, "address_getter", "address_loader"),
            (AssociationRead, "association_getter", "association_loader"),
            (EmployeeRead, "employee_getter", "employee_loader"),
            (EngagementRead, "engagement_getter", "engagement_loader"),
            (ManagerRead, "manager_getter", "manager_loader"),
            (OwnerRead, "owner_getter", "owner_loader"),
            (OrganisationUnitRead, "org_unit_getter", "org_unit_loader"),
            (ITSystemRead, "itsystem_getter", "itsystem_loader"),
            (ITUserRead, "ituser_getter", "ituser_loader"),
            (KLERead, "kle_getter", "kle_loader"),
            (LeaveRead, "leave_getter", "leave_loader"),
            (RelatedUnitRead, "rel_unit_getter", "rel_unit_loader"),
            (RoleRead, "role_getter", "role_loader"),
        ]
        resolver_map: dict[Any, Any] = {
            model: {
                "getter": getter,
                "loader": loader,
            }
            for model, getter, loader in _resolver_tuples
        }
        loader_name = resolver_map[self.model]["loader"]
        getter_name = resolver_map[self.model]["getter"]
        loader = info.context[loader_name]
        getter = info.context[getter_name]
        return await generic_resolver(
            loader,
            getter,
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class FacetResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(FacetRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        parents: ParentUUIDsFilterType = None,
        parent_user_keys: ParentUserKeysFilterType = None,
    ):
        filter = FacetFilter(
            uuids=uuids,
            user_keys=user_keys,
            parents=parents,
            parent_user_keys=parent_user_keys,
        )
        return await facet_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ClassResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ClassRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        facets: FacetUUIDsFilterType = None,
        facet_user_keys: FacetUserKeysFilterType = None,
        parents: ParentUUIDsFilterType = None,
        parent_user_keys: ParentUserKeysFilterType = None,
    ):
        filter = ClassFilter(
            uuids=uuids,
            user_keys=user_keys,
            facets=facets,
            facet_user_keys=facet_user_keys,
            parents=parents,
            parent_user_keys=parent_user_keys,
        )
        return await class_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class AddressResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AddressRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        address_types: AddressTypeUUIDsFilterType = None,
        address_type_user_keys: AddressTypeUserKeysFilterType = None,
        employees: EmployeeUUIDsFilterType = None,
        engagements: EngagementUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = AddressFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            address_types=address_types,
            address_type_user_keys=address_type_user_keys,
            employees=employees,
            engagements=engagements,
            org_units=org_units,
        )
        return await address_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class AssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AssociationRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
        association_types: AssociationTypeUUIDsFilterType = None,
        association_type_user_keys: AssociationTypeUserKeysFilterType = None,
        it_association: ITAssociation = None,
    ):
        filter = AssociationFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
            association_types=association_types,
            association_type_user_keys=association_type_user_keys,
            it_association=it_association,
        )
        return await association_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ConfigurationResolver(PagedResolver):
    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        limit: LimitType = None,
        cursor: CursorType = None,
        identifiers: Annotated[
            list[str] | None,
            strawberry.argument(description=gen_filter_string("Key", "identifiers")),
        ] = None,
    ):
        filter = ConfigurationFilter(
            identifiers=identifiers,
        )
        return await configuration_resolver(
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class EmployeeResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EmployeeRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        cpr_numbers: CPRNumberFilterType = None,
    ):
        filter = EmployeeFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            cpr_numbers=cpr_numbers,
        )
        return await employee_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class EngagementResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = EngagementFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await engagement_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class FileResolver(PagedResolver):
    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        file_store: Annotated[
            FileStore,
            strawberry.argument(
                description=dedent(
                    """\
                    File Store enum deciding which file-store to fetch files from.
                """
                )
            ),
        ],
        limit: LimitType = None,
        cursor: CursorType = None,
        file_names: Annotated[
            list[str] | None,
            strawberry.argument(
                description=gen_filter_string("Filename", "file_names")
            ),
        ] = None,
    ):
        filter = FileFilter(
            file_store=file_store,
            file_names=file_names,
        )
        return await file_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class HealthResolver(PagedResolver):
    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        limit: LimitType = None,
        cursor: CursorType = None,
        identifiers: Annotated[
            list[str] | None,
            strawberry.argument(
                description=gen_filter_string("Healthcheck identifiers", "identifiers")
            ),
        ] = None,
    ):
        filter = HealthFilter(
            identifiers=identifiers,
        )
        return await health_resolver(
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ITSystemResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITSystemRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
    ):
        filter = ITSystemFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
        )
        return await it_system_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ManagerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ManagerRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = ManagerFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await manager_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class OwnerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OwnerRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = OwnerFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await owner_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class OrganisationUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OrganisationUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        parents: ParentUUIDsFilterType = UNSET,
        hierarchies: HierarchiesUUIDsFilterType = None,
    ):
        filter = OrganisationUnitFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            parents=parents,
            hierarchies=hierarchies,
        )
        return await organisation_unit_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ITUserResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITUserRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = ITUserFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await it_user_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class KLEResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(KLERead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = KLEFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            org_units=org_units,
        )
        return await kle_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class LeaveResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(LeaveRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = LeaveFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await leave_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class RelatedUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RelatedUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = RelatedUnitFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            org_units=org_units,
        )
        return await related_unit_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class RoleResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RoleRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        filter = RoleFilter(
            uuids=uuids,
            user_keys=user_keys,
            from_date=from_date,
            to_date=to_date,
            employees=employees,
            org_units=org_units,
        )
        return await role_resolver(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )
