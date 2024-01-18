# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Mapping from data models to data resolvers."""
from typing import Any

from .models import ClassRead
from .models import FacetRead
from ramodels.mo import EmployeeRead
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


loader_map: dict[Any, str] = {
    FacetRead: "facet_loader",
    ClassRead: "class_loader",
    AddressRead: "address_loader",
    AssociationRead: "association_loader",
    EmployeeRead: "employee_loader",
    EngagementRead: "engagement_loader",
    ManagerRead: "manager_loader",
    OwnerRead: "owner_loader",
    OrganisationUnitRead: "org_unit_loader",
    ITSystemRead: "itsystem_loader",
    ITUserRead: "ituser_loader",
    KLERead: "kle_loader",
    LeaveRead: "leave_loader",
    RelatedUnitRead: "rel_unit_loader",
    RoleRead: "role_loader",
}
