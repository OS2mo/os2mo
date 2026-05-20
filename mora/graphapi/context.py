# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeAlias
from uuid import UUID

from fastramqpi.ramqp import AMQPSystem
from strawberry import Info
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from mora import db
from mora.auth.keycloak.models import Token
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationRead
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
from mora.graphapi.graphql_utils import LoadKey
from mora.graphapi.models import AddressRead
from mora.graphapi.models import ClassRead
from mora.graphapi.models import FacetRead
from mora.graphapi.models import RoleBindingRead


@dataclass
class MOLoaders:
    org_loader: DataLoader[int, OrganisationRead]
    org_unit_loader: DataLoader[LoadKey, list[OrganisationUnitRead]]
    employee_loader: DataLoader[LoadKey, list[EmployeeRead]]
    engagement_loader: DataLoader[LoadKey, list[EngagementRead]]
    kle_loader: DataLoader[LoadKey, list[KLERead]]
    address_loader: DataLoader[LoadKey, list[AddressRead]]
    leave_loader: DataLoader[LoadKey, list[LeaveRead]]
    association_loader: DataLoader[LoadKey, list[AssociationRead]]
    rolebinding_loader: DataLoader[LoadKey, list[RoleBindingRead]]
    ituser_loader: DataLoader[LoadKey, list[ITUserRead]]
    manager_loader: DataLoader[LoadKey, list[ManagerRead]]
    owner_loader: DataLoader[LoadKey, list[OwnerRead]]
    class_loader: DataLoader[LoadKey, list[ClassRead]]
    rel_unit_loader: DataLoader[LoadKey, list[RelatedUnitRead]]
    facet_loader: DataLoader[LoadKey, list[FacetRead]]
    itsystem_loader: DataLoader[LoadKey, list[ITSystemRead]]
    access_log_read_loader: DataLoader[UUID, list[UUID]]
    actor_name_loader: DataLoader[UUID, str | None]


@dataclass
class MOContext(BaseContext):
    get_token: Callable[[], Awaitable[Token]]
    amqp_system: AMQPSystem
    session: db.AsyncSession
    dataloaders: MOLoaders


MOInfo: TypeAlias = Info[MOContext, None]
