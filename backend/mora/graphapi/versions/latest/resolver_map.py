# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Mapping from data models to data resolvers."""

from typing import Any

from strawberry.dataloader import DataLoader

from mora.graphapi.context import MOInfo
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
from mora.graphapi.versions.latest.graphql_utils import LoadKey

from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead


def get_dataloader(info: MOInfo, model: type[Any]) -> DataLoader[LoadKey, list[Any]]:
    mapping: dict[type[Any], DataLoader[LoadKey, list[Any]]] = {
        FacetRead: info.context.facet_loader,
        ClassRead: info.context.class_loader,
        AddressRead: info.context.address_loader,
        AssociationRead: info.context.association_loader,
        EmployeeRead: info.context.employee_loader,
        EngagementRead: info.context.engagement_loader,
        ManagerRead: info.context.manager_loader,
        OwnerRead: info.context.owner_loader,
        OrganisationUnitRead: info.context.org_unit_loader,
        ITSystemRead: info.context.itsystem_loader,
        ITUserRead: info.context.ituser_loader,
        KLERead: info.context.kle_loader,
        LeaveRead: info.context.leave_loader,
        RelatedUnitRead: info.context.rel_unit_loader,
        RoleBindingRead: info.context.rolebinding_loader,
    }
    return mapping[model]
