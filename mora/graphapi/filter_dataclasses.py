# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The filters in `filters`, as dataclasses a predicate can be handed."""

import dataclasses
from functools import cache
from typing import TYPE_CHECKING
from typing import Any

from strawberry.types import get_object_definition
from strawberry.types.base import WithStrawberryObjectDefinition
from strawberry.types.field import StrawberryField

from . import filters


@cache
def dataclass_of(filter_class: type[WithStrawberryObjectDefinition]) -> type:
    """Converts a Strawberry input class to an equivalent dataclass."""

    def default(field: StrawberryField) -> Any:
        if field.default_factory is not dataclasses.MISSING:
            return dataclasses.field(default_factory=field.default_factory)
        return dataclasses.field(default=field.default)

    return dataclasses.make_dataclass(
        filter_class.__name__,
        fields=[
            (field.name, field.type, default(field))
            for field in get_object_definition(filter_class, strict=True).fields
        ],
    )


def strawberry2dataclass(filter: Any) -> Any:
    """Converts a Strawberry input instance to an equivalent dataclass instance."""
    if filter is None:
        return None
    if not dataclasses.is_dataclass(filter):
        return filter
    filter_class: type = type(filter)
    dataclass = dataclass_of(filter_class)
    return dataclass(
        **{
            field.name: strawberry2dataclass(getattr(filter, field.name))
            for field in dataclasses.fields(filter)
        }
    )


if TYPE_CHECKING:
    # The dataclasses hold the same fields as the filters they are made from,
    # and unlike the generated classes a type checker can see them
    from .filters import AddressFilter as AddressFilterData
    from .filters import AssociationFilter as AssociationFilterData
    from .filters import BaseFilter as BaseFilterData
    from .filters import ClassFilter as ClassFilterData
    from .filters import EmployeeFilter as EmployeeFilterData
    from .filters import EmployeeFiltered as EmployeeFilteredData
    from .filters import EngagementFilter as EngagementFilterData
    from .filters import FacetFilter as FacetFilterData
    from .filters import ITSystemFilter as ITSystemFilterData
    from .filters import ITUserFilter as ITUserFilterData
    from .filters import KLEFilter as KLEFilterData
    from .filters import LeaveFilter as LeaveFilterData
    from .filters import ManagerFilter as ManagerFilterData
    from .filters import OrganisationUnitFilter as OrganisationUnitFilterData
    from .filters import OrganisationUnitFiltered as OrganisationUnitFilteredData
    from .filters import OwnerFilter as OwnerFilterData
    from .filters import RegistrationFilter as RegistrationFilterData
    from .filters import RelatedUnitFilter as RelatedUnitFilterData
    from .filters import RoleBindingFilter as RoleBindingFilterData
else:
    AddressFilterData = dataclass_of(filters.AddressFilter)
    AssociationFilterData = dataclass_of(filters.AssociationFilter)
    BaseFilterData = dataclass_of(filters.BaseFilter)
    ClassFilterData = dataclass_of(filters.ClassFilter)
    EmployeeFilterData = dataclass_of(filters.EmployeeFilter)
    EmployeeFilteredData = dataclass_of(filters.EmployeeFiltered)
    EngagementFilterData = dataclass_of(filters.EngagementFilter)
    FacetFilterData = dataclass_of(filters.FacetFilter)
    ITSystemFilterData = dataclass_of(filters.ITSystemFilter)
    ITUserFilterData = dataclass_of(filters.ITUserFilter)
    KLEFilterData = dataclass_of(filters.KLEFilter)
    LeaveFilterData = dataclass_of(filters.LeaveFilter)
    ManagerFilterData = dataclass_of(filters.ManagerFilter)
    OrganisationUnitFilterData = dataclass_of(filters.OrganisationUnitFilter)
    OrganisationUnitFilteredData = dataclass_of(filters.OrganisationUnitFiltered)
    OwnerFilterData = dataclass_of(filters.OwnerFilter)
    RegistrationFilterData = dataclass_of(filters.RegistrationFilter)
    RelatedUnitFilterData = dataclass_of(filters.RelatedUnitFilter)
    RoleBindingFilterData = dataclass_of(filters.RoleBindingFilter)
