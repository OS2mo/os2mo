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
        FacetRead: info.context.dataloaders.facet_loader,
        ClassRead: info.context.dataloaders.class_loader,
        AddressRead: info.context.dataloaders.address_loader,
        AssociationRead: info.context.dataloaders.association_loader,
        EmployeeRead: info.context.dataloaders.employee_loader,
        EngagementRead: info.context.dataloaders.engagement_loader,
        ManagerRead: info.context.dataloaders.manager_loader,
        OwnerRead: info.context.dataloaders.owner_loader,
        OrganisationUnitRead: info.context.dataloaders.org_unit_loader,
        ITSystemRead: info.context.dataloaders.itsystem_loader,
        ITUserRead: info.context.dataloaders.ituser_loader,
        KLERead: info.context.dataloaders.kle_loader,
        LeaveRead: info.context.dataloaders.leave_loader,
        RelatedUnitRead: info.context.dataloaders.rel_unit_loader,
        RoleBindingRead: info.context.dataloaders.rolebinding_loader,
    }
    return mapping[model]
