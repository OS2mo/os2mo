# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Mapping from data models to data resolvers."""

from typing import Any

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import OwnerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead

from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead

# TODO: Encode this relation using Annotated types
# FacetRead = Annotated[FacetRead, FacetResolver(...)]
# Then later extract the resolver from the type using typing.get_args
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
    (RoleBindingRead, "rolebinding_getter", "rolebinding_loader"),
]
resolver_map: dict[Any, Any] = {
    model: {
        "getter": getter,
        "loader": loader,
    }
    for model, getter, loader in _resolver_tuples
}
